from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.services.jwt_utils import decode_access_token
from app.services.user import get_user_by_id
from app.models.user import User
from app.services.db import get_db_session
from typing import Optional


def get_current_user(
    token: str, db: Optional[Session] = Depends(get_db_session)
) -> User:
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user
