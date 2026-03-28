import os
import httpx
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends

from app.models import Employee
from app.schemas.background import Create
from app.models.background import Background
from uuid import uuid4
from app.database import get_db
from datetime import datetime
from app.core.deps import require_admin


load_dotenv()
BASE_URL = os.getenv("BACKGROUND_URL")
router = APIRouter(prefix="/background", tags=["background"])

@router.post("")
async def create(data: Create, admin=Depends(require_admin), db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == data.employeeId).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    url = f"{BASE_URL}/background-checks"

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json={
            "employeeId": emp.employee_code,
            "firstName": emp.first_name,
            "lastName": emp.last_name,
            "dateOfBirth": str(emp.birth_date),
        })

    if response.status_code not in [200, 201]:
        try:
            detail = response.json()
        except:
            detail = response.text

        raise HTTPException(
            status_code=response.status_code,
            detail=detail
        )

    res = response.json()

    checks = Background(
        id=uuid4(),
        employee_id=emp.id,
        check_id=res["checkId"],
        status=res["status"],
        requested_at=datetime.fromisoformat(
            res["createdAt"].replace("Z", "+00:00")
        ),
    )

    db.add(checks)
    db.commit()

    return res

@router.get("")
async def  get_checks(employeeId: str, admin=Depends(require_admin), db: Session = Depends(get_db)):
    checks = db.query(Background).filter(Background.employee_id == employeeId).order_by(Background.requested_at.desc()).all()

    backgrounds = [
        {
            "checkId": c.check_id,
            "status": c.status,
            "requested_at": c.requested_at,
            "completed_at": c.completed_at
        }
        for c in checks
    ]

    return {"backgrounds": backgrounds}


@router.get("/sync")
async def  sync_checks(employeeId: str, admin=Depends(require_admin), db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == employeeId).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/background-checks?employeeId={emp.employee_code}")

    if response.status_code != 200:
        try:
            detail = response.json()
        except:
            detail = response.text

        raise HTTPException(
            status_code=response.status_code,
            detail=detail
        )

    data = response.json()

    for item in data["checks"]:
        check_id = item["checkId"]

        existing = db.query(Background).filter(
            Background.check_id == check_id
        ).first()

        requested_at = datetime.fromisoformat(
            item["createdAt"].replace("Z", "+00:00")
        )

        completed_at = None
        if item.get("completedAt"):
            completed_at = datetime.fromisoformat(
                item["completedAt"].replace("Z", "+00:00")
            )

        if existing:
            existing.status = item["status"]
            existing.requested_at = requested_at
            existing.completed_at = completed_at
        else:
            db.add(Background(
                employee_id=emp.id,
                check_id=check_id,
                status=item["status"],
                requested_at=requested_at,
                completed_at=completed_at
            ))

    db.commit()

    return {"message": "Sync completed"}

@router.get("/{checkId}")
async def get_check(checkId: str, admin=Depends(require_admin), db: Session = Depends(get_db)):
    check = db.query(Background).filter(Background.check_id == checkId).first()

    if check and check.status != "pending" and check.criminal_record is not None:
        return check

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/background-checks/{checkId}")

    if response.status_code != 200:
        try:
            detail = response.json()
        except:
            detail = response.text

        raise HTTPException(
            status_code=response.status_code,
            detail=detail
        )

    data = response.json()

    requested_at = datetime.fromisoformat(
        data["createdAt"].replace("Z", "+00:00")
    )

    completed_at = None
    if data.get("completedAt"):
        completed_at = datetime.fromisoformat(
            data["completedAt"].replace("Z", "+00:00")
        )

    if check:
        check.status = data["status"]
        check.criminal_record = data.get("criminalRecord")
        check.education_verified = data.get("educationVerified")
        check.employment_verified = data.get("employmentVerified")
        check.credit_score = data.get("creditScore")
        check.completed_at = completed_at
    else:
        check = Background(
            check_id=data["checkId"],
            status=data["status"],
            criminal_record=data.get("criminalRecord"),
            education_verified=data.get("educationVerified"),
            employment_verified=data.get("employmentVerified"),
            credit_score=data.get("creditScore"),
            requested_at=requested_at,
            completed_at=completed_at
        )
        db.add(check)

    db.commit()

    return data