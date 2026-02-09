from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID


class RoomCreateResponse(BaseModel):
    room_code: str = Field(..., example="K7Q9A")
    host_token: str
    expires_at: datetime | None


class RoomJoinResponse(BaseModel):
    room_code: str


class RoomPublic(BaseModel):
    room_code: str
    created_at: datetime
    expires_at: datetime | None

    class Config:
        from_attributes = True
