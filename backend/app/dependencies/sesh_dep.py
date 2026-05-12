import asyncio
from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from datetime import datetime
from sqlalchemy.orm import joinedload
from app.db.sessions import get_db
from app.schemas.sessions_sch import Session as SessionModel
from app.models.sessions import SessionContext

def _update_last_seen(session_id, db):
    try:
        db.query(SessionModel).filter(
            SessionModel.id == session_id
        ).update({"last_seen_at": datetime.utcnow()})
        db.commit()
    except:
        pass
# AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
async def get_current_session(
    x_session_token: str = Header(..., alias="X-Session-Token"),
    db: Session = Depends(get_db)
) -> SessionContext:
    session = (
        db.query(SessionModel)
        .options(joinedload(SessionModel.room))
        .filter(SessionModel.session_token == x_session_token)
        .first()
    )
    # print("SESH DATA",session.id)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session token")

    # session.last_seen_at = datetime.utcnow()
    # db.commit()
    asyncio.create_task(
        asyncio.to_thread(_update_last_seen, session.id, db)
    )
    return SessionContext(
        session_id = session.id,
        room_id=session.room_id,
        role=session.role,
        last_seen_at=session.last_seen_at,
        room_code=session.room.room_code,
    )