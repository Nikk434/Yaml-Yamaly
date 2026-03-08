from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
import secrets
from datetime import datetime
from app.models.rooms import RoomCreateResponse, RoomJoinRequest, RoomPublicResponse
from app.service.room_service import create_room as create_room_service
from app.db.sessions import get_db
from app.schemas.rooms_sch import Room
router = APIRouter()

@router.post("/rooms", response_model=RoomCreateResponse, status_code=201)
def create_room(db: Session = Depends(get_db)):
    room = create_room_service(db)

    return RoomCreateResponse(
        room_code=room.room_code,
        owner_secret=room.owner_secret,
        created_at=room.created_at,
        expires_at=room.expires_at
    )

@router.post("/join", response_model=RoomPublicResponse, status_code=200)
def join_room(payload: RoomJoinRequest, db: Session = Depends(get_db)):
    room = (
        db.query(Room)
        .filter(Room.room_code == payload.room_code)
        .first()
    )

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    session_token = secrets.token_urlsafe(32)

    session = Session(
        room_id=room.id,
        role="contributor",
        session_token=session_token,
        created_at=datetime.utcnow()
    )

    db.add(session)
    db.commit()

    return RoomPublicResponse(
        room_code=room.room_code,
        session_token=session_token,
        created_at=room.created_at,
        expires_at=room.expires_at
    )