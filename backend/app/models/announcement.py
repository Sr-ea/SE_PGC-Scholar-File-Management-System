import uuid

from app.core.database import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship


class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String, default="general")  # general / reminder / warning / deadline

    # Who receives it — stored as a filter snapshot
    recipient_filter = Column(JSONB, nullable=True)
    # e.g. {"batch": "Batch 5", "school": "UST", "status": "active"}
    # null = sent to ALL scholars

    created_at = Column(DateTime, server_default=func.now())
    scheduled_at = Column(DateTime, nullable=True)  # for future scheduling

    recipients = relationship("AnnouncementReceipt", back_populates="announcement")


class AnnouncementReceipt(Base):
    __tablename__ = "announcement_receipts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    announcement_id = Column(
        UUID(as_uuid=True), ForeignKey("announcements.id"), nullable=False
    )
    scholar_id = Column(UUID(as_uuid=True), ForeignKey("scholars.id"), nullable=False)

    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)

    announcement = relationship("Announcement", back_populates="recipients")
