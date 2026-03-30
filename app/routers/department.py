from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import UUID
from sqlalchemy import and_

from app.core.deps import require_admin
from app.database import get_db
from app.models import Department, Employee
from app.schemas.department import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse,
)

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.post("", response_model=DepartmentResponse)
def create_department(data: DepartmentCreate, admin=Depends(require_admin),db: Session = Depends(get_db)):
    existing = db.query(Department).filter(
        and_(Department.deleted_at.is_(None),
        Department.name.ilike(data.name.strip()))
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="이미 존재하는 부서명입니다.")

    dept = Department(
        name=data.name,
        description=data.description,
        manager_id=data.manager_id,
    )

    db.add(dept)
    db.commit()

    return dept

@router.get("")
def get_departments(admin=Depends(require_admin), db: Session = Depends(get_db)):
    results = (
        db.query(
            Department,
            Employee.first_name,
            Employee.last_name
        )
        .outerjoin(Employee, Department.manager_id == Employee.id)
        .filter(Department.deleted_at == None)
        .all()
    )

    return {"departments": [
        {
            "id": dept.id,
            "name": dept.name,
            "description": dept.description,
            "created_at": dept.created_at,
            "manager_id": dept.manager_id,
            "manager_full_name": f"{last} {first}" if last and first else "-"
        }
        for dept, first, last in results
    ]}

@router.get("/{department_id}")
def get_department_detail(department_id: UUID, admin=Depends(require_admin), db: Session = Depends(get_db)):
    dept = (
        db.query(Department)
        .filter(
            and_(
                Department.id == department_id,
                Department.deleted_at == None
            )
        )
        .first()
    )

    if not dept:
        raise HTTPException(status_code=404, detail="부서를 찾을 수 없습니다.")

    dept.manager_full_name = ""
    if dept.manager_id:
        manager = db.query(Employee).filter(Employee.id == dept.manager_id).first()
        dept.manager_full_name = f"{manager.last_name} {manager.first_name}"

    employees = (
        db.query(Employee)
        .filter(Employee.department_id == department_id)
        .all()
    )

    dept.employees = employees
    return dept

@router.patch("/{department_id}", response_model=DepartmentResponse)
def update_department(
    department_id: UUID,
    data: DepartmentUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)
):
    dept = db.query(Department).filter(
        and_(Department.id == department_id,
        Department.deleted_at == None)
    ).first()

    if not dept:
        raise HTTPException(status_code=404, detail="부서를 찾을 수 없습니다.")

    if data.name is not None:
        # 중복 체크
        existing = db.query(Department).filter(
            and_(Department.deleted_at.is_(None),
            Department.id != department_id,
            Department.name.ilike(data.name.strip()))
        ).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"이미 존재하는 부서명입니다."
            )

        dept.name = data.name

    if data.description is not None:
        dept.description = data.description

    dept.manager_id = data.manager_id

    db.commit()
    db.refresh(dept)

    return dept

@router.delete("/{dept_id}")
def remove_department(dept_id: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    department = db.query(Department).filter(
        and_(Department.id == dept_id,
        Department.deleted_at.is_(None))
    ).first()

    if not department:
        raise HTTPException(status_code=404, detail="부서를 찾을 수 없습니다.")

    db.query(Employee).filter(
        Employee.department_id == dept_id,
        Employee.deleted_at is None
    ).update(
        {Employee.department_id: None},
        synchronize_session=False
    )

    department.deleted_at = datetime.utcnow()

    db.commit()

    return {"message": "부서가 삭제되었습니다."}