from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.services.jwt_utils import decode_access_token
from app.services.user import get_user_by_id
from app.models.user import User
from app.services.db import get_db_session
from typing import Optional


async def get_current_user(
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

    # Convert string user_id to integer if it's a string with a numeric format
    # Handle both plain numeric strings and prefixed IDs like "user_id_123"
    if isinstance(user_id, str):
        if user_id.isdigit():
            user_id = int(user_id)
        elif "_" in user_id:
            # Try to extract numeric part from formats like "user_id_123"
            parts = user_id.split("_")
            if parts and parts[-1].isdigit():
                user_id = int(parts[-1])

    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user
    return user
