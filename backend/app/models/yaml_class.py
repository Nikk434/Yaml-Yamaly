#yaml_class
# - id = should start form 0 and should be continous
# - class = must be string, can of any length, spaces allowed 
# - status = entered, approved, discarded, needs review 
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional
from enum import Enum

class ClassStatus(str, Enum):
    entered = "entered"
    needs_review = "needs_review"
    approved = "approved"
    discarded = "discarded"

class YamlClassBase(BaseModel):
    raw_class_name: str = Field(..., min_length=1)
    normalized_class_name: str = Field(..., min_length=1)
    status: ClassStatus

    review_reason: Optional[str] = None
    matched_class_id: Optional[UUID] = None

class YamlClassCreateRequest(BaseModel):
    class_name: str = Field(..., min_length=1)

class YamlClassCreateInternal(YamlClassBase):
    room_id: UUID
    created_by_session_id: UUID

class YamlClassReviewRequest(BaseModel):
    status: ClassStatus

    review_reason: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status": "approved",
                "review_reason": "manual approval"
            }
        }

class YamlClassResponse(YamlClassBase):
    id: UUID
    room_id: UUID
    created_by_session_id: UUID

    created_at: datetime
    reviewed_at: Optional[datetime]

class YamlClassExport(BaseModel):
    id: int = Field(..., ge=0)
    class_name: str
