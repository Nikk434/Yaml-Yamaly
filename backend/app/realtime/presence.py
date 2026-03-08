from sqlalchemy import func
from app.schemas.sessions_sch import Session

async def emit_room_counts(sio, db, room_id: int, room_code: str):
    counts = (
        db.query(Session.role, func.count(Session.id))
        .filter(Session.room_id == room_id)
        .group_by(Session.role)
        .all()
    )

    result = {"host": 0, "contributor": 0}

    for role, count in counts:
        result[role.value] = count

    await sio.emit(
        "room_presence_update",
        {
            "room_code": room_code,
            "host_count": result["host"],
            "contributor_count": result["contributor"]
        },
        room=room_code
    )
