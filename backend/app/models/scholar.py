from sqlalchemy import Column, String, Integer, ForeignKey, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

class Scholar(Base):
    __tablename__ = "scholars"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)

    # Batch & program info
    batch_number = Column(String, nullable=True)
    year_level = Column(String, nullable=True)
    course = Column(String, nullable=True)
    school = Column(String, nullable=True)
    status = Column(String, default="active")  # active, inactive, graduate

    # Personal info
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    middle_name = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    address = Column(String, nullable=True)
    contact_number = Column(String, nullable=True)

    # Relationship back to User
    user = relationship("User", back_populates="scholar")
