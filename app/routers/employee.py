from uuid import uuid4
from sqlalchemy import and_
from datetime import datetime
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException

from app.database import get_db
from app.models.employee import Employee
from app.models.auth import Auth
from app.models.background import Background
from app.models.department import Department
from app.core.deps import get_current_user, require_admin
from app.schemas.employee import (
    EmployeeCreate,
    EmployeeResponse,
    EmployeeUpdate
)


router = APIRouter(prefix="/employees", tags=["employees"])

pwd_context = CryptContext(schemes=["bcrypt"])

def hash_password(password: str):
    return pwd_context.hash(password)


@router.post("")
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
        first_name=data.first_name,
        last_name=data.last_name,
        employee_code=data.employee_code,
        phone=data.phone,
        birth_date=data.birth_date,
        department_id=data.department_id,
        position=data.position,
        hire_date=data.hire_date,
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


@router.get("")
def get_employees(admin=Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(Employee).filter(Employee.deleted_at.is_(None)).all()

@router.get("/admin/list")
def get_admin_list(admin=Depends(require_admin),db: Session = Depends(get_db)):
    list = db.query(Employee.id, Employee.last_name, Employee.first_name, Auth.email, Employee.employee_code) \
        .join(Auth, Auth.user_id == Employee.id) \
        .filter(Auth.role == "ADMIN", Auth.is_active == True, Employee.deleted_at.is_(None))\
        .all()

    return [r._asdict() for r in list]


@router.get("/me")
def get_my_info(user=Depends(get_current_user), db: Session = Depends(get_db)):
    emp, auth = (
        db.query(Employee, Auth)
        .join(Auth, Auth.user_id == Employee.id)
        .filter(Employee.id == user["user_id"], Employee.deleted_at.is_(None))
        .first()
    )

    if not emp:
        raise HTTPException(status_code=404, detail="User not found")

    dept = None
    if emp.department_id:
        dept = (
            db.query(Department)
            .filter(Department.id == emp.department_id, Department.deleted_at.is_(None))
            .first()
        )

    return {
        "id": emp.id,
        "name": f"{emp.last_name} {emp.first_name}",
        "position": emp.position,
        "department_id": emp.department_id,
        "department_name": dept.name if dept else None,
        "email": auth.email,
        "role": auth.role,
        "is_active": auth.is_active,
        "phone": emp.phone,
        "hire_date": emp.hire_date,
        "birth_date": emp.birth_date,
        "employee_code": emp.employee_code,
    }


@router.get("/full")
def get_full_employees(admin=Depends(require_admin), db: Session = Depends(get_db)):
    result = (
        db.query(
            Employee.id.label("id"),
            Employee.last_name,
            Employee.first_name,
            Employee.position,
            Employee.phone,
            Employee.employee_code,
            Employee.hire_date,
            Employee.department_id,
            Employee.status,
            Auth.email,
            Auth.role,
            Department.name.label("department_name"),
        )
        .join(Auth, Auth.user_id == Employee.id)
        .outerjoin(Department, and_(Department.id == Employee.department_id, Department.deleted_at == None))
        .filter(Employee.deleted_at.is_(None))
        .all()
    )

    return [
        {
            "id": r.id,
            "name": f"{r.last_name} {r.first_name}",
            "position": r.position,
            "email": r.email,
            "role": r.role,
            "phone": r.phone,
            "employee_code": r.employee_code,
            "hire_date": r.hire_date,
            "department_id": r.department_id,
            "department_name": r.department_name,
            "status": r.status,
        }
        for r in result
    ]


@router.get("/{employee_id}")
def get_employee(employee_id: str,
                 user=Depends(get_current_user),
                 db: Session = Depends(get_db)):

    if user["role"] != "ADMIN" and user["user_id"] != employee_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    emp = db.query(Employee).filter(Employee.id == employee_id, Employee.deleted_at.is_(None)).first()
    if not emp:
        raise HTTPException(404)

    auth = db.query(Auth).filter(Auth.user_id == emp.id, Auth.deleted_at.is_(None)).first()

    latest_check = db.query(Background).filter(Background.employee_id == employee_id).order_by(Background.requested_at.desc()).first()

    dept = None
    if emp.department_id:
        dept = db.query(Department.name).filter(Department.id == emp.department_id, Department.deleted_at.is_(None)).first()

    return {
        "email": auth.email,
        "role": auth.role,
        "is_active": auth.is_active,
        "first_name": emp.first_name,
        "department_id": emp.department_id,
        "department_name": dept.name if dept else None,
        "position": emp.position,
        "birth_date": emp.birth_date,
        "status": emp.status,
        "employee_code": emp.employee_code,
        "phone": emp.phone,
        "id": emp.id,
        "last_name": emp.last_name,
        "name": f"{emp.last_name} {emp.first_name}",
        "hire_date": emp.hire_date,
        "latest_background": latest_check,
    }


@router.patch("/{employee_id}")
def update_employee(
    employee_id: str,
    data: EmployeeUpdate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user["role"] != "ADMIN" and user["user_id"] != employee_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    emp = db.query(Employee).filter(Employee.id == employee_id, Employee.deleted_at.is_(None)).first()
    auth = db.query(Auth).filter(Auth.user_id == employee_id, Auth.deleted_at.is_(None)).first()

    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    # employee 업데이트
    for key, value in data.dict(exclude_unset=True).items():
        if hasattr(emp, key):
            setattr(emp, key, value)

    # auth 업데이트
    if auth:
        if data.status == "RESIGNED" and emp.status != "RESIGNED":
            auth.is_active = False

        if data.role is not None:
            auth.role = data.role

        if data.is_active is not None:
            auth.is_active = data.is_active

    db.commit()

    return {"message": "Updated"}

@router.delete("/{employee_id}")
def delete_employee(employee_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    employee = (
        db.query(Employee)
        .filter(Employee.id == employee_id, Employee.deleted_at.is_(None))
        .first()
    )

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    auth = (
        db.query(Auth)
        .filter(Auth.user_id == employee_id, Auth.deleted_at.is_(None))
        .first()
    )

    now = datetime.utcnow()

    employee.deleted_at = now

    if auth:
        auth.deleted_at = now

    db.commit()

    return {"message": "직원 삭제 완료"}