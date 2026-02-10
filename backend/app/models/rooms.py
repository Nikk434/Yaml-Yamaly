#rooms
# - id (UUID)
# - room_code (human, joinable)
# - owner_secret (LONG-LIVED, private)
# - created_at
# - expires_at (optional)
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
import re
from pydantic import BaseModel, Field, field_validator

ROOM_CODE_REGEX = r'^[A-Za-z0-9!@#$%&*]{6}$'

class RoomCreate(BaseModel):
    expires_at: datetime | None = None

class RoomCreateResponse(BaseModel):
    room_code: str
    owner_secret: str
    created_at: datetime
    expires_at: datetime | None

class RoomJoinRequest(BaseModel):
    room_code: str = Field(..., min_length=6, max_length=6)

    @field_validator("room_code")
    @classmethod
    def validate_room_code(cls, v: str) -> str:
        if not re.match(ROOM_CODE_REGEX, v):
            raise ValueError("Invalid room code format")
        return v

class RoomPublicResponse(BaseModel):
    room_code: str
    created_at: datetime
    expires_at: datetime | None

class RoomOwnerAuth(BaseModel):
    room_code: str
    owner_secret: str
