from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.auth import Auth
from app.core.security import verify_password, create_access_token
from app.schemas.auth import LoginRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(Auth).filter(Auth.email == data.email).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid email")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Wrong password")

    token = create_access_token({
        "user_id": str(user.user_id),
        "role": user.role
    })

    return {"access_token": token, "token_type": "bearer"}

@router.get("/{user_id}")
def get_auth(user_id: str, db: Session = Depends(get_db)):
    return db.query(Auth).filter(Auth.user_id == user_id).first()

@router.put("/{user_id}")
def update_auth(user_id: str, data: dict, db: Session = Depends(get_db)):
    auth = db.query(Auth).filter(Auth.user_id == user_id).first()

    if not auth:
        raise HTTPException(404)

    if "is_active" in data:
        auth.is_active = data["is_active"]

    db.commit()
    return {"message": "updated"}