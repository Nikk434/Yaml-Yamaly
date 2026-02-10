from enum import Enum
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class SessionRole(str, Enum):
    host = "host"
    contributor = "contributor"

class SessionBase(BaseModel):
    id: UUID
    room_id: UUID
    role: SessionRole
    created_at: datetime
    last_seen_at: datetime

    class Config:
        from_attributes = True

class SessionCreateResponse(BaseModel):
    session_token: str
    role: SessionRole
    created_at: datetime

class SessionContext(BaseModel):
    room_id: UUID
    role: SessionRole
    last_seen_at: datetime

class SessionValidateRequest(BaseModel):
    session_token: str
