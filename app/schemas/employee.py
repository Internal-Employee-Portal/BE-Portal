from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional
from datetime import date


# 생성 요청
class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    employee_code: Optional[str] = None
    phone: Optional[str] = None
    department_id: Optional[UUID] = None
    position: Optional[str] = None

    hire_date: date
    birth_date: Optional[date] = None

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
    last_name: Optional[str] = None
    first_name: Optional[str] = None
    employee_code: Optional[str] = None
    phone: Optional[str] = None
    birth_date: Optional[date] = None
    department_id: Optional[UUID] = None
    position: Optional[str] = None
    hire_date: Optional[date] = None
    status: Optional[str] = None

    role: Optional[str] = None
    is_active: Optional[bool] = None