import uuid

from app.core.database import Base
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Scholar(Base):
    __tablename__ = "scholars"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True
    )

    # Program info
    batch_number = Column(String, nullable=True)
    year_level = Column(String, nullable=True)
    course = Column(String, nullable=True)
    school = Column(String, nullable=True)
    status = Column(String, default="active")  # active / inactive / graduate
    student_type = Column(String, default="regular")  # regular / irregular
    date_enrolled = Column(Date, nullable=True)

    # Personal info
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    middle_name = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    place_of_birth = Column(String, nullable=True)
    sex = Column(String, nullable=True)
    civil_status = Column(String, nullable=True)
    religion = Column(String, nullable=True)
    address = Column(String, nullable=True)
    contact_number = Column(String, nullable=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="scholar")
    academic_records = relationship("AcademicRecord", back_populates="scholar")
    documents = relationship("Document", back_populates="scholar")
    program_history = relationship("ProgramHistory", back_populates="scholar")
    pending_changes = relationship("PendingChange", back_populates="scholar")
