from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.sessions import get_db
from app.schemas.sessions_sch import Session as SessionModel
from app.models.sessions import SessionContext

def get_current_session(
    x_session_token: str = Header(..., alias="X-Session-Token"),
    db: Session = Depends(get_db)
) -> SessionContext:
    session = (
        db.query(SessionModel)
        .filter(SessionModel.session_token == x_session_token)
        .first()
    )
    # print("SESH DATA",session.id)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session token")

    session.last_seen_at = datetime.utcnow()
    db.commit()

    return SessionContext(
        session_id = session.id,
        room_id=session.room_id,
        role=session.role,
        last_seen_at=session.last_seen_at
    )
