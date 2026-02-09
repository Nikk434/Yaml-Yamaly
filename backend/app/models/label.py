# models/label.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Enum,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base
from sqlalchemy.dialects.postgresql import UUID


class LabelStatus(str, enum.Enum):
    active = "active"
    needs_review = "needs_review"
    deprecated = "deprecated"
    merged = "merged"


class Label(Base):
    __tablename__ = "labels"

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    room_id = Column(
        UUID(as_uuid=True),
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    display_name = Column(
        String(128),
        nullable=False
    )

    canonical_name = Column(
        String(128),
        nullable=False
    )

    normalized_name = Column(
        String(128),
        nullable=False
    )

    status = Column(
        Enum(LabelStatus),
        nullable=False,
        default=LabelStatus.active
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    created_by_session = Column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id"),
        nullable=True
    )

    room = relationship("Room", backref="labels")
    session = relationship("Session", backref="labels")

    __table_args__ = (
        UniqueConstraint(
            "room_id",
            "normalized_name",
            name="uq_label_room_normalized"
        ),
        UniqueConstraint(
            "room_id",
            "canonical_name",
            name="uq_label_room_canonical"
        ),
    )
