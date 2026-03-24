from pydantic import BaseModel, EmailStr
from uuid import UUID
from typing import Optional


# 생성 요청
class EmployeeCreate(BaseModel):
    name: str
    department_id: Optional[UUID]
    position: Optional[str]

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
    name: Optional[str]
    department_id: Optional[UUID]
    position: Optional[str]