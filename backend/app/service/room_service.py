from sqlalchemy.exc import IntegrityError
from app.utils.room_code_gen import generate_owner_secret,generate_room_code
from app.schemas.rooms_sch import Room
# from app.service import 
def create_room(db):
    owner_secret = generate_owner_secret()

    for _ in range(5):
        room_code = generate_room_code()
        try:
            room = Room(
                room_code=room_code,
                owner_secret=owner_secret
            )
            db.add(room)
            db.commit()
            db.refresh(room)
            return room
        except IntegrityError:
            db.rollback()

    raise RuntimeError("Could not generate unique room code")
