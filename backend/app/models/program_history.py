import uuid

from app.core.database import Base
from sqlalchemy import Column, Date, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class ProgramHistory(Base):
    __tablename__ = "program_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scholar_id = Column(UUID(as_uuid=True), ForeignKey("scholars.id"), nullable=False)
    recorded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    course = Column(String, nullable=False)
    school = Column(String, nullable=False)
    year_level = Column(String, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)  # null = current program
    reason = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    scholar = relationship("Scholar", back_populates="program_history")
