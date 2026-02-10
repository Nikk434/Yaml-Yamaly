from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session as DBSession
from app.db.session import get_db
from app.service.room_service import create_room
from app.schemas.room import RoomCreateResponse
from app.schemas.room import JoinRoomRequest,JoinRoomResponse
from app.models.room import Room
from app.models.session import SessionRole
from app.models.session import Session as SessionModel, SessionRole

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.post(
    "",
    response_model=RoomCreateResponse,
    status_code=status.HTTP_201_CREATED
)
def create_room_endpoint(db: DBSession  = Depends(get_db)):
    return create_room(db)

@router.post("/join", response_model=JoinRoomResponse)
def join_room(payload: JoinRoomRequest, db: DBSession  = Depends(get_db)):
    room = (
        db.query(Room)
        .filter(Room.room_code == payload.room_code)
        .first()
    )

    if not room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found"
        )

    # if not room.is_active:
    #     raise HTTPException(
    #         status_code=status.HTTP_410_GONE,
    #         detail="Room is closed"
    #     )

    session = SessionModel(
        room_id=room.id,
        role=SessionRole.contributor
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return JoinRoomResponse(
        session_id=session.id,
        role=session.role
    )