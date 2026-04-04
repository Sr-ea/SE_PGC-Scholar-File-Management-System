import uuid

from app.core.database import Base
from sqlalchemy import Column, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class ProspectusGrade(Base):
    __tablename__ = "prospectus_grades"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    academic_record_id = Column(
        UUID(as_uuid=True), ForeignKey("academic_records.id"), nullable=False
    )

    subject_code = Column(String, nullable=True)
    subject_name = Column(String, nullable=False)
    units = Column(Numeric(4, 1), nullable=True)
    grade = Column(String, nullable=True)  # "1.0", "2.5", "INC", etc.
    status = Column(String, nullable=True)  # passed / failed / INC / unposted

    academic_record = relationship("AcademicRecord", back_populates="grades")
