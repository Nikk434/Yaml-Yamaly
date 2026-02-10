import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.sessions import SessionRole

class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    room_id = Column(
        UUID(as_uuid=True),
        ForeignKey("rooms.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    session_token = Column(String(128), unique=True, nullable=False, index=True)

    role = Column(
        Enum(SessionRole, name="session_role"),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    last_seen_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    room = relationship("Room", backref="sessions")

