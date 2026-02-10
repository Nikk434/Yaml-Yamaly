from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from app.db.sessions import get_db
from app.schemas.yaml_class import YamlClass, ClassStatusDB
from app.models.yaml_class import (
    YamlClassCreateRequest,
    YamlClassResponse,
    YamlClassReviewRequest
)
from app.dependencies.sesh_dep import get_current_session

router = APIRouter(prefix="/classes", tags=["classes"])

@router.post("", response_model=YamlClassResponse, status_code=201)
def create_class(
    payload: YamlClassCreateRequest,
    session_token: str = Header(..., alias="X-Session-Token"),
    db: Session = Depends(get_db),
):
    session = get_current_session(session_token, db)

    if session.role not in ("contributor", "host"):
        raise HTTPException(status_code=403, detail="Invalid role")

    normalized = payload.class_name.strip().lower()

    existing = db.query(YamlClass).filter(
        YamlClass.room_id == session.room_id,
        YamlClass.normalized_class_name == normalized,
        YamlClass.status == ClassStatusDB.approved
    ).first()

    status_value = ClassStatusDB.entered
    review_reason = None
    matched_id = None

    if existing:
        status_value = ClassStatusDB.needs_review
        review_reason = "exact duplicate"
        matched_id = existing.id

    obj = YamlClass(
        room_id=session.room_id,
        created_by_session_id=session.session_id,
        raw_class_name=payload.class_name,
        normalized_class_name=normalized,
        status=status_value,
        review_reason=review_reason,
        matched_class_id=matched_id
    )

    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@router.patch("/{class_id}", response_model=YamlClassResponse)
def review_class(
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
    return obj