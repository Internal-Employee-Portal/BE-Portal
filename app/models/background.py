import uuid
from sqlalchemy import Column, String, Date, TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

class Background(Base):
    __tablename__ = "background"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    check_id = Column(String(100), nullable=False)
    status = Column(String(100), nullable=False)
    requested_at = Column(TIMESTAMP, nullable=False)

    criminal_record = Column(Boolean)
    education_verified = Column(Boolean)
    employment_verified = Column(Boolean)
    credit_score = Column(String(100))
    completed_at = Column(TIMESTAMP)
