from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from fastapi.security import HTTPBearer

from app.core.security import SECRET_KEY, ALGORITHM

security = HTTPBearer()


def get_current_user(token=Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

def require_admin(user=Depends(get_current_user)):
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin only")
    return user