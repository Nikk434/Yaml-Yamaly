from sqlalchemy import (
    Column,
    String,
    Enum,
    DateTime,
    ForeignKey,
    Text
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.db.base import Base
from enum import Enum as PyEnum
class ClassStatusDB(str, PyEnum):
    entered = "entered"
    needs_review = "needs_review"
    approved = "approved"
    discarded = "discarded"

class YamlClass(Base):
    __tablename__ = "yaml_classes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    room_id = Column(
        UUID(as_uuid=True),
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    created_by_session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    raw_class_name = Column(String, nullable=False)
    normalized_class_name = Column(String, nullable=False, index=True)

    status = Column(
        Enum(ClassStatusDB, name="class_status_enum"),
        nullable=False,
        default=ClassStatusDB.entered,
        index=True
    )

    review_reason = Column(Text, nullable=True)

    matched_class_id = Column(
        UUID(as_uuid=True),
        ForeignKey("yaml_classes.id"),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    reviewed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )
