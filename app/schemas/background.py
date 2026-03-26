from pydantic import BaseModel


class Create(BaseModel):
    employeeId: str
    firstName: str
    lastName: str
    dateOfBirth: str