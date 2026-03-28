from jose import jwt, JWTError
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer
from fastapi import Depends, HTTPException
from app.database import get_db
from app.core.security import SECRET_KEY, ALGORITHM
from app.models import Employee, Auth

security = HTTPBearer()


def get_current_user(
    token=Depends(security),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        emp, auth = db.query(Employee, Auth) \
            .join(Auth, Auth.user_id == Employee.id) \
            .filter(Employee.id == user_id) \
            .first()

        if not emp or not auth:
            raise HTTPException(status_code=401, detail="User not found")

        if not auth.is_active:
            raise HTTPException(status_code=401, detail="Inactive user")

        return {
            "user_id": user_id,
            "role": auth.role
        }

    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

def require_admin(user=Depends(get_current_user)):
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin only")
    return user