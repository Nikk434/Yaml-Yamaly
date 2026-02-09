from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.service.room_service import create_room
from app.schemas.room import RoomCreateResponse

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.post(
    "",
    response_model=RoomCreateResponse,
    status_code=status.HTTP_201_CREATED
)
def create_room_endpoint(db: Session = Depends(get_db)):
    return create_room(db)
