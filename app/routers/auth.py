from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.auth import Auth
from app.core.security import verify_password, create_access_token, hash_password
from app.core.deps import get_current_user
from app.schemas.auth import LoginRequest, ChangePasswordRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(Auth).filter(Auth.email == data.email, Auth.deleted_at.is_(None)).first()

    if not user:
        raise HTTPException(status_code=400, detail="이메일 또는 비밀번호가 올바르지 않습니다.")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="비활성화 계정입니다. 관리자에게 문의하세요.")

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="이메일 또는 비밀번호가 올바르지 않습니다.")

    token = create_access_token({
        "user_id": str(user.user_id),
        "role": user.role
    })

    return {"access_token": token, "token_type": "bearer"}

@router.get("/{user_id}")
def get_auth(user_id: str, db: Session = Depends(get_db)):
    return db.query(Auth).filter(Auth.user_id == user_id).first()

@router.patch("/change-password")
def change_password(
    body: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: Auth = Depends(get_current_user),  # 로그인 유저
):
    auth = (
        db.query(Auth)
        .filter(Auth.user_id == current_user["user_id"], Auth.deleted_at.is_(None))
        .first()
    )

    if not verify_password(body.current_password, auth.password_hash):
        raise HTTPException(status_code=400, detail="현재 비밀번호가 일치하지 않습니다.")

    if body.new_password != body.confirm_password:
        raise HTTPException(status_code=400, detail="비밀번호 확인이 일치하지 않습니다.")

    if verify_password(body.new_password, auth.password_hash):
        raise HTTPException(status_code=400, detail="기존 비밀번호와 동일합니다.")

    auth.password_hash = hash_password(body.new_password)

    db.commit()

    return {"message": "비밀번호 변경 완료"}

@router.patch("/{user_id}")
def update_auth(user_id: str, data: dict, db: Session = Depends(get_db)):
    auth = db.query(Auth).filter(Auth.user_id == user_id).first()

    if not auth:
        raise HTTPException(404)

    if "is_active" in data:
        auth.is_active = data["is_active"]

    db.commit()
    return {"message": "updated"}