from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from .auth import decode_access_token
from .db import get_session
from .crud import get_user_by_username
from sqlmodel import Session


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def get_current_user(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    username = payload.get("sub")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )
    user = get_user_by_username(session, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return user


def teacher_required(current_user=Depends(get_current_user)):
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="Teacher role required")
    return current_user


def student_required(current_user=Depends(get_current_user)):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Student role required")
    return current_user
