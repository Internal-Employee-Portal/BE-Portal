import uuid
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    manager_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    description = Column(String(255), nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    deleted_at = Column(TIMESTAMP,  nullable=True)