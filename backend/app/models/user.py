import enum
import uuid

from app.core.database import Base
from sqlalchemy import Boolean, Column, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship


class Role(str, enum.Enum):
    scholar = "scholar"
    evaluator = "evaluator"
    admin = "admin"


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=True)
    role = Column(Enum(Role), nullable=False)
    is_active = Column(Boolean, default=True)

    scholar = relationship("Scholar", back_populates="user", uselist=False)
