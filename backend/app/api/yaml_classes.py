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
from app.models.sessions import SessionContext
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
    curr_session: SessionContext = Depends(get_current_session),
):
    import time
    t = {}
    _start = time.perf_counter()
    t["session_lookup"] = time.perf_counter()

    if curr_session.role not in ("contributor", "host"):
        raise HTTPException(status_code=403, detail="Invalid role")

    normalized = payload.class_name.strip().lower()

    status_value = ClassStatusDB.entered
    review_reason = None
    matched_id = None

    # exact duplicate
    existing = db.query(YamlClass).filter(
        YamlClass.room_id == curr_session.room_id,
        YamlClass.normalized_class_name == normalized,
    ).first()
    t["exact_dup_query"] = time.perf_counter()

    if existing:
        status_value = ClassStatusDB.needs_review
        review_reason = "exact duplicate"
        matched_id = existing.id

    # fuzzy duplicate
    if not existing:
        existing_class = db.query(YamlClass).filter(
            YamlClass.room_id == curr_session.room_id,
        ).all()
        t["fuzzy_fetch_query"] = time.perf_counter()

        fuzzy_matches = fuzzy_match_class(normalized, existing_class)
        t["fuzzy_compute"] = time.perf_counter()

        if fuzzy_matches:
            matched_id, matched_name, score = fuzzy_matches[0]
            status_value = ClassStatusDB.needs_review
            review_reason = f"fuzzy match ({score}%) with '{matched_name}'"

    obj = YamlClass(
        room_id=curr_session.room_id,
        created_by_session_id=curr_session.session_id,
        raw_class_name=payload.class_name,
        normalized_class_name=normalized,
        status=status_value,
        review_reason=review_reason,
        matched_class_id=matched_id
    )
    db.add(obj)
    db.commit()
    t["db_insert"] = time.perf_counter()

    t["room_query"] = time.perf_counter()

    await emit_class_created(curr_session.room_code, obj)
    t["emit"] = time.perf_counter()

    # --- print breakdown ---
    checkpoints = ["session_lookup", "exact_dup_query", "fuzzy_fetch_query",
                   "fuzzy_compute", "db_insert", "room_query", "emit"]
    prev = _start
    print("\n--- create_class profiling ---")
    for key in checkpoints:
        if key not in t:
            continue
        elapsed = (t[key] - prev) * 1000
        total = (t[key] - _start) * 1000
        print(f"  {key:<22} {elapsed:>7.1f}ms   (total {total:.1f}ms)")
        prev = t[key]
    print(f"  {'TOTAL':<22} {(time.perf_counter() - _start)*1000:>7.1f}ms")
    print("------------------------------\n")

    return obj


@router.patch("/{class_id}", response_model=YamlClassResponse)
async def review_class(
    class_id: UUID,
    payload: YamlClassReviewRequest,
    session_token: str = Header(..., alias="X-Session-Token"),
    db: Session = Depends(get_db),
    curr_session: SessionContext = Depends(get_current_session),
):
    if curr_session.role != "host":
        raise HTTPException(status_code=403, detail="Host only")

    obj = db.query(YamlClass).filter(
        YamlClass.id == class_id,
        YamlClass.room_id == curr_session.room_id
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

    await emit_class_reviewed(curr_session.room_code, obj)

    return obj


@router.get("", response_model=list[YamlClassResponse])
async def list_classes(
    session_token: str = Header(..., alias="X-Session-Token"),
    db: Session = Depends(get_db),
    curr_session: SessionContext = Depends(get_current_session),
):
    classes = (
        db.query(YamlClass)
        .filter(YamlClass.room_id == curr_session.room_id)
        .order_by(YamlClass.created_at.asc())
        .all()
    )

    return classes


@router.get("/export")
async def export_yaml(
    session_token: str = Header(..., alias="X-Session-Token"),
    db: Session = Depends(get_db),
    curr_session: SessionContext = Depends(get_current_session),
):
    if curr_session.role != "host":
        raise HTTPException(status_code=403, detail="Host only")

    classes = db.query(YamlClass).filter(
        YamlClass.room_id == curr_session.room_id
    ).all()

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