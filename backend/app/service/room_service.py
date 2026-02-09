from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models.room import Room
from app.models.session import Session as RoomSession, SessionRole
from app.utils.room import generate_room_code, generate_host_token


def create_room(db: Session):
    for _ in range(5):  # retry on rare room_code collision
        room = Room(
            room_code=generate_room_code(),
            host_token=generate_host_token()
        )

        db.add(room)
        db.commit()
        db.refresh(room)
        try:
            db.flush()  # get room.id
            break
        except IntegrityError:
            db.rollback()
    else:
        raise RuntimeError("Failed to generate unique room code")

    # create host session
    session = RoomSession(
        room_id=room.id,
        role=SessionRole.host
    )

    db.add(session)
    db.commit()
    db.refresh(room)
    db.refresh(session)

    return {
        "room_code": room.room_code,
        "host_token": room.host_token,
        "session_id": session.id,
        "expires_at": room.expires_at
    }
