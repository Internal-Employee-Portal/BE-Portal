from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional
from datetime import date


# 생성 요청
class EmployeeCreate(BaseModel):
    name: str
    department_id: Optional[UUID] = None
    position: Optional[str] = None

    hire_date: Optional[date] = None

    email: EmailStr
    password: str
    role: str = "USER"


# 응답
class EmployeeResponse(BaseModel):
    id: UUID
    name: str
    position: Optional[str]

    class Config:
        from_attributes = True


# 수정
class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    department_id: Optional[UUID] = None
    email: Optional[str] = None
    position: Optional[str] = None
    hire_date: Optional[date] = None
    status: Optional[str] = None

    role: Optional[str] = None
    is_active: Optional[bool] = None