from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from models.session import SessionRole


class SessionCreateResponse(BaseModel):
    session_id: UUID
    role: SessionRole


class SessionPublic(BaseModel):
    id: UUID
    role: SessionRole
    created_at: datetime
    last_seen_at: datetime

    class Config:
        from_attributes = True
