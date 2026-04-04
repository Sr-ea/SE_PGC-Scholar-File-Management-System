import uuid

from app.core.database import Base
from sqlalchemy import Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class AcademicRecord(Base):
    __tablename__ = "academic_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scholar_id = Column(UUID(as_uuid=True), ForeignKey("scholars.id"), nullable=False)
    reviewed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    school_year = Column(String, nullable=False)  # e.g. "2024-2025"
    semester = Column(String, nullable=False)  # "1st" / "2nd" / "summer"
    student_type = Column(String, default="regular")
    remarks_status = Column(String, nullable=True)  # complete / unposted / INC / failed
    unposted_count = Column(String, default="0")
    inc_count = Column(String, default="0")
    failed_count = Column(String, default="0")

    submission_status = Column(
        String, default="draft"
    )  # draft / pending / approved / rejected
    submitted_at = Column(DateTime, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    scholar = relationship("Scholar", back_populates="academic_records")
    grades = relationship(
        "ProspectusGrade",
        back_populates="academic_record",
        cascade="all, delete-orphan",
    )
    documents = relationship("Document", back_populates="academic_record")
