# models/alias.py

import uuid
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Alias(Base):
    __tablename__ = "aliases"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    room_id = Column(
        UUID(as_uuid=True),
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    label_id = Column(
        Integer,
        ForeignKey("labels.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    alias_name = Column(
        String(128),
        nullable=False
    )

    normalized_alias = Column(
        String(128),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    label = relationship("Label", backref="aliases")
    room = relationship("Room", backref="aliases")

    __table_args__ = (
        UniqueConstraint(
            "room_id",
            "normalized_alias",
            name="uq_alias_room_normalized"
        ),
    )
