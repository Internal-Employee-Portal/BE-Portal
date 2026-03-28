from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID


class DepartmentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    manager_id: Optional[UUID] = None


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    manager_id: Optional[UUID] = None


class EmployeeMini(BaseModel):
    first_name: str
    last_name: str
    role: str
    email: str
    phone: Optional[str] = None

    class Config:
        from_attributes = True


class DepartmentResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    manager_id: Optional[UUID]

    class Config:
        from_attributes = True


class DepartmentDetailResponse(DepartmentResponse):
    employees: List[EmployeeMini] = []