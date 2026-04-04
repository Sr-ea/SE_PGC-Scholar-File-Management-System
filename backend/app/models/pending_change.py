import uuid

from app.core.database import Base
from sqlalchemy import Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship


class PendingChange(Base):
    __tablename__ = "pending_changes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scholar_id = Column(UUID(as_uuid=True), ForeignKey("scholars.id"), nullable=False)
    submitted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    claimed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    claimed_at = Column(DateTime, nullable=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    change_type = Column(String, nullable=False)  # profile / grades / documents
    payload = Column(JSONB, nullable=False)  # the actual changes as JSON
    status = Column(
        String, default="pending"
    )  # pending / approved / rejected / more_info

    submitted_at = Column(DateTime, server_default=func.now())
    reviewed_at = Column(DateTime, nullable=True)
    evaluator_note = Column(Text, nullable=True)

    scholar = relationship("Scholar", back_populates="pending_changes")
