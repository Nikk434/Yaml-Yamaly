from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class AliasPublic(BaseModel):
    id: UUID
    alias_name: str
    created_at: datetime

    class Config:
        from_attributes = True
