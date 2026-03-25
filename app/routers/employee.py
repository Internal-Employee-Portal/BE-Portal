from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4

from app.database import get_db
from app.models.employee import Employee
from app.models.auth import Auth

from app.schemas.employee import (
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate
)

from app.core.deps import get_current_user, require_admin
from passlib.context import CryptContext

router = APIRouter(prefix="/employees", tags=["employees"])

pwd_context = CryptContext(schemes=["bcrypt"])


def hash_password(password: str):
    return pwd_context.hash(password)


# 🔹 직원 생성 (관리자만)
@router.post("/")
def create_employee(data: EmployeeCreate,
                    admin=Depends(require_admin),
                    db: Session = Depends(get_db)):

    if data.role not in ["ADMIN", "USER"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    # 이메일 중복 체크
    existing = db.query(Auth).filter(Auth.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    employee = Employee(
        id=uuid4(),
        name=data.name,
        department_id=data.department_id,
        position=data.position
    )

    db.add(employee)
    db.flush()

    auth = Auth(
        id=uuid4(),
        user_id=employee.id,
        email=data.email,
        password_hash=hash_password(data.password),
        role=data.role
    )

    db.add(auth)
    db.commit()

    return {"message": "Employee created"}


# 🔹 전체 조회
@router.get("/", response_model=list[EmployeeResponse])
def get_employees(db: Session = Depends(get_db)):
    return db.query(Employee).all()


@router.get("/me")
def get_my_info(user=Depends(get_current_user), db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == user["user_id"]).first()
    return emp

@router.get("/full")
def get_full_employees(db: Session = Depends(get_db)):
    result = db.query(Employee, Auth).join(Auth, Auth.user_id == Employee.id).all()

    return [
        {
            "id": emp.id,
            "name": emp.name,
            "position": emp.position,
            "email": auth.email,
            "role": auth.role
        }
        for emp, auth in result
    ]


# 🔹 개별 조회
@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(employee_id: str,
                 user=Depends(get_current_user),
                 db: Session = Depends(get_db)):

    if user["role"] != "ADMIN" and user["user_id"] != employee_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    emp = db.query(Employee).filter(Employee.id == employee_id).first()

    if not emp:
        raise HTTPException(404)

    return emp


# 🔹 수정
@router.put("/{employee_id}")
def update_employee(employee_id: str,
                    data: EmployeeUpdate,
                    user=Depends(get_current_user),
                    db: Session = Depends(get_db)):

    if user["role"] != "ADMIN" and user["user_id"] != employee_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # if "role" in data:
    #     auth.role = data["role"]
    #
    # if "email" in data:
    #     auth.email = data["email"]
    #
    # if "is_active" in data:
    #     auth.is_active = data["is_active"]

    emp = db.query(Employee).filter(Employee.id == employee_id).first()

    if not emp:
        raise HTTPException(404)

    for key, value in data.dict(exclude_unset=True).items():
        setattr(emp, key, value)

    db.commit()

    return {"message": "Updated"}