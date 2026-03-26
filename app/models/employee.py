import uuid
from sqlalchemy import Column, String, Date, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"))
    position = Column(String(100))
    hire_date = Column(Date)
    status = Column(String(20), default="ACTIVE")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP,  nullable=True)