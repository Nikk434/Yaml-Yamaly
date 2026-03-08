from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from thefuzz import process, fuzz
from fastapi.responses import Response
import yaml


from app.db.sessions import get_db
from app.schemas.rooms_sch import Room
from app.schemas.yaml_class import YamlClass, ClassStatusDB
from app.models.yaml_class import (
    YamlClassCreateRequest,
    YamlClassResponse,
    YamlClassReviewRequest
)
from app.dependencies.sesh_dep import get_current_session
from app.realtime.class_events import emit_class_created, emit_class_reviewed

FUZZY_THRESHOLD = 60

router = APIRouter(prefix="/classes", tags=["classes"])


def fuzzy_match_class(normalized_name: str, existing_classes):
    choices = {cls.normalized_class_name: cls.id for cls in existing_classes}


    results = process.extract(
        normalized_name,
        choices.keys(),
        scorer=fuzz.partial_ratio,
        limit=None
    )

    matches = [
        (choices[name], name, score)
        for name, score in results
        if score >= FUZZY_THRESHOLD
    ]

    return matches


@router.post("", response_model=YamlClassResponse, status_code=201)
async def create_class(
    payload: YamlClassCreateRequest,
    session_token: str,
    db: Session = Depends(get_db),
):
    session = get_current_session(session_token, db)

    if session.role not in ("contributor", "host"):
        raise HTTPException(status_code=403, detail="Invalid role")

    normalized = payload.class_name.strip().lower()

    status_value = ClassStatusDB.entered
    review_reason = None
    matched_id = None

    # exact duplicate
    existing = db.query(YamlClass).filter(
        YamlClass.room_id == session.room_id,
        YamlClass.normalized_class_name == normalized,
        YamlClass.status == ClassStatusDB.approved
    ).first()

    if existing:
        status_value = ClassStatusDB.needs_review
        print("")
        review_reason = "exact duplicate"
        matched_id = existing.id

    # fuzzy duplicate
    if not existing:
        print("Entered fuzzy match\n")
        approved_classes = db.query(YamlClass).filter(
            YamlClass.room_id == session.room_id,
            YamlClass.status == ClassStatusDB.approved
        ).all()
        print("Approved classes:", [c.normalized_class_name for c in approved_classes])

        fuzzy_matches = fuzzy_match_class(normalized, approved_classes)

        if fuzzy_matches:
            matched_id, matched_name, score = fuzzy_matches[0]

            status_value = ClassStatusDB.needs_review
            review_reason = f"fuzzy match ({score}%) with '{matched_name}'"
        print("exited fuzzy match\n")
        
    obj = YamlClass(
        room_id=session.room_id,
        created_by_session_id=session.session_id,
        raw_class_name=payload.class_name,
        normalized_class_name=normalized,
        status=status_value,
        review_reason=review_reason,
        matched_class_id=matched_id
    )
    print("\nOBJ",obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)

    room = db.query(Room).filter(Room.id == session.room_id).first()

    await emit_class_created(room.room_code, obj)

    return obj


@router.patch("/{class_id}", response_model=YamlClassResponse)
async def review_class(
    class_id: UUID,
    payload: YamlClassReviewRequest,
    session_token: str = Header(..., alias="X-Session-Token"),
    db: Session = Depends(get_db),
):
    session = get_current_session(session_token, db)

    if session.role != "host":
        raise HTTPException(status_code=403, detail="Host only")

    obj = db.query(YamlClass).filter(
        YamlClass.id == class_id,
        YamlClass.room_id == session.room_id
    ).first()

    if not obj:
        raise HTTPException(status_code=404, detail="Class not found")

    if payload.status not in (ClassStatusDB.approved, ClassStatusDB.discarded):
        raise HTTPException(status_code=400, detail="Invalid status transition")

    obj.status = payload.status
    obj.review_reason = payload.review_reason
    obj.reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(obj)

    room = db.query(Room).filter(Room.id == session.room_id).first()

    await emit_class_reviewed(room.room_code, obj)

    return obj


@router.get("", response_model=list[YamlClassResponse])
def list_classes(
    session_token: str = Header(..., alias="X-Session-Token"),
    db: Session = Depends(get_db),
):
    session = get_current_session(session_token, db)

    classes = (
        db.query(YamlClass)
        .filter(YamlClass.room_id == session.room_id)
        .order_by(YamlClass.created_at.asc())
        .all()
    )

    return classes

@router.get("/export")
def export_yaml(
    session_token: str = Header(..., alias="X-Session-Token"),
    db: Session = Depends(get_db),
):
    session = get_current_session(session_token, db)

    if session.role != "host":
        raise HTTPException(status_code=403, detail="Host only")

    classes = db.query(YamlClass).filter(
        YamlClass.room_id == session.room_id
    ).all()

    # block export if unreviewed exist
    pending = [
        c for c in classes
        if c.status in (ClassStatusDB.entered, ClassStatusDB.needs_review)
    ]

    if pending:
        raise HTTPException(
            status_code=400,
            detail="Some classes still need approval before export"
        )

    approved = [
        c for c in classes
        if c.status == ClassStatusDB.approved
    ]

    approved.sort(key=lambda x: x.created_at)

    names = {i: c.raw_class_name for i, c in enumerate(approved)}

    yaml_data = {
        "train": "",
        "val": "",
        "test": "",
        "nc": len(names),
        "names": names
    }

    yaml_string = yaml.dump(yaml_data, sort_keys=False)

    return Response(
        content=yaml_string,
        media_type="text/yaml",
        headers={
            "Content-Disposition": "attachment; filename=data.yaml"
        }
    )
