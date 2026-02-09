# schemas/label.py

from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID
from models.label import LabelStatus


class LabelCreateRequest(BaseModel):
    display_name: str = Field(..., example="Play City")


class SimilarLabel(BaseModel):
    id: int
    display_name: str
    similarity: float


class LabelCreateResponse(BaseModel):
    id: int
    display_name: str
    status: LabelStatus
    similar_to: list[SimilarLabel] = []


class LabelPublic(BaseModel):
    id: int
    display_name: str
    canonical_name: str
    status: LabelStatus
    created_at: datetime

    class Config:
        from_attributes = True
