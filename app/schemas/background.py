from pydantic import BaseModel


class Create(BaseModel):
    employeeId: str