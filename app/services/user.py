from datetime import datetime, timezone
from sqlalchemy.orm import Session
from typing import Optional
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.auth_utils import hash_password, verify_password


def create_user(db: Session, user_data: UserCreate) -> User:
    hashed_pw = hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pw,
        role=user_data.role,
        bio=user_data.bio,
        profile_picture_url=user_data.profile_picture_url,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
    user = get_user_by_id(db, user_id)
    if user:
        for field, value in user_data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        db.commit()
        db.refresh(user)
    return user


def delete_user(db: Session, user_id: int) -> bool:
    user = get_user_by_id(db, user_id)
    if user:
        user.deleted_at = datetime.now(timezone.utc)
        db.commit()
        return True
    return False


def undelete_user(db: Session, user_id: int) -> bool:
    user = get_user_by_id(db, user_id)
    if user and user.deleted_at:
        user.deleted_at = None
        db.commit()
        return True
    return False


def update_last_login(db: Session, user_id: int) -> bool:
    user = get_user_by_id(db, user_id)
    if user:
        user.last_login = datetime.now(timezone.utc)
        db.commit()
        return True
    return False


def change_password(
    db: Session, user_id: int, old_password: str, new_password: str
) -> bool:
    user = get_user_by_id(db, user_id)
    if user and verify_password(old_password, user.hashed_password):
        user.hashed_password = hash_password(new_password)
        db.commit()
        return True
    return False


def activate_user(db: Session, user_id: int) -> bool:
    user = get_user_by_id(db, user_id)
    if user and not user.is_active:
        user.is_active = True
        db.commit()
        return True
    return False


def deactivate_user(db: Session, user_id: int) -> bool:
    user = get_user_by_id(db, user_id)
    if user and user.is_active:
        user.is_active = False
        db.commit()
        return True
    return False
