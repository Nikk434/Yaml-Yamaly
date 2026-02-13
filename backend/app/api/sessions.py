from fastapi import APIRouter, Depends, HTTPException, Cookie
from sqlalchemy.orm import Session
from datetime import datetime
import secrets
from sqlalchemy import func
from app.db.sessions import get_db
from app.schemas.rooms_sch import Room
from app.schemas.sessions_sch import Session as SessionModel
from app.models.sessions import SessionCreateResponse, SessionRole

router = APIRouter()

@router.post("/sessions/host", response_model=SessionCreateResponse)
def create_host_session(
    room_code: str,
    owner_secret: str,
    db: Session = Depends(get_db)
):
    room = (
        db.query(Room)
        .filter(
            Room.room_code == room_code,
            Room.owner_secret == owner_secret
        )
        .first()
    )

    if not room:
        raise HTTPException(status_code=403, detail="Invalid room or owner secret")

    session = SessionModel(
        room_id=room.id,
        session_token=secrets.token_urlsafe(48),
        role=SessionRole.host,
        created_at=datetime.utcnow(),
        last_seen_at=datetime.utcnow()
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return SessionCreateResponse(
        session_token=session.session_token,
        role=session.role,
        created_at=session.created_at
    )

@router.post("/sessions/join", response_model=SessionCreateResponse)
def create_contributor_session(
    room_code: str,
    db: Session = Depends(get_db)
):
    room = (
        db.query(Room)
        .filter(Room.room_code == room_code)
        .first()
    )

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    session = SessionModel(
        room_id=room.id,
        session_token=secrets.token_urlsafe(48),
        role=SessionRole.contributor,
        created_at=datetime.utcnow(),
        last_seen_at=datetime.utcnow()
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return SessionCreateResponse(
        session_token=session.session_token,
        role=session.role,
        created_at=session.created_at
    )

@router.get("/sessions/count")
def get_room_session_info(
    room_code: str,
    session_token: str,
    db: Session = Depends(get_db)
):
    room = (
        db.query(Room)
        .filter(Room.room_code == room_code)
        .first()
    )

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    caller_session = (
        db.query(SessionModel)
        .filter(
            SessionModel.session_token == session_token,
            SessionModel.room_id == room.id
        )
        .first()
    )

    if not caller_session:
        raise HTTPException(status_code=403, detail="Invalid session for this room")

    counts = (
        db.query(SessionModel.role, func.count(SessionModel.id))
        .filter(SessionModel.room_id == room.id)
        .group_by(SessionModel.role)
        .all()
    )

    result = {
        "host": 0,
        "contributor": 0
    }

    for role, count in counts:
        result[role.value] = count

    return {
        "room_code": room_code,
        "your_role": caller_session.role,
        "host_count": result["host"],
        "contributor_count": result["contributor"]
    }