import uuid

from app.core.database import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scholar_id = Column(UUID(as_uuid=True), ForeignKey("scholars.id"), nullable=False)
    academic_record_id = Column(
        UUID(as_uuid=True), ForeignKey("academic_records.id"), nullable=True
    )

    doc_type = Column(
        String, nullable=False
    )  # COR / ROG / explanation_letter / completion_form / other
    file_name = Column(String, nullable=False)  # original filename shown to user
    storage_path = Column(String, nullable=False)  # path inside Supabase Storage
    file_size = Column(Integer, nullable=True)  # bytes
    mime_type = Column(String, nullable=True)  # image/jpeg, application/pdf, etc.
    is_verified = Column(Boolean, default=False)

    uploaded_at = Column(DateTime, server_default=func.now())

    scholar = relationship("Scholar", back_populates="documents")
    academic_record = relationship("AcademicRecord", back_populates="documents")
