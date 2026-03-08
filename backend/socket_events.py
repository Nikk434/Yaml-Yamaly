from datetime import datetime
from app.db.sessions import SessionLocal
from app.schemas.rooms_sch import Room
from app.schemas.sessions_sch import Session
from app.realtime.presence import emit_room_counts

def register_socket_events(sio):

    @sio.event
    async def join_room(sid, data):
        print("\n ENTERED SOCKET SECTION \n")
        db = SessionLocal()

        session_token = data.get("session_token")
        room_code = data.get("room_code")

        session = (
            db.query(Session)
            .join(Room)
            .filter(
                Session.session_token == session_token,
                Room.room_code == room_code
            )
            .first()
        )

        if not session:
            db.close()
            return

        session.socket_sid = sid
        session.last_seen_at = datetime.utcnow()
        db.commit()

        await sio.enter_room(sid, room_code)
        await emit_room_counts(sio,db, session.room_id, room_code)

        db.close()
        