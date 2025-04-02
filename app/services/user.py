from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.auth_utils import hash_password, verify_password


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
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
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalars().first()


async def update_user(
    db: AsyncSession, user_id: int, user_data: UserUpdate
) -> Optional[User]:
    user = await get_user_by_id(db, user_id)
    if user:
        for field, value in user_data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        await db.commit()
        await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    user = await get_user_by_id(db, user_id)
    if user:
        user.deleted_at = datetime.now(timezone.utc)
        await db.commit()
        return True
    return False


async def undelete_user(db: AsyncSession, user_id: int) -> bool:
    user = await get_user_by_id(db, user_id)
    if user and user.deleted_at:
        user.deleted_at = None
        await db.commit()
        return True
    return False


async def update_last_login(db: AsyncSession, user_id: int) -> bool:
    user = await get_user_by_id(db, user_id)
    if user:
        user.last_login = datetime.now(timezone.utc)
        await db.commit()
        return True
    return False


async def change_password(
    db: AsyncSession, user_id: int, old_password: str, new_password: str
) -> bool:
    user = await get_user_by_id(db, user_id)
    if user and verify_password(old_password, user.hashed_password):
        user.hashed_password = hash_password(new_password)
        await db.commit()
        return True
    return False


async def activate_user(db: AsyncSession, user_id: int) -> bool:
    user = await get_user_by_id(db, user_id)
    if user and not user.is_active:
        user.is_active = True
        await db.commit()
        return True
    return False


async def deactivate_user(db: AsyncSession, user_id: int) -> bool:
    user = await get_user_by_id(db, user_id)
    if user and user.is_active:
        user.is_active = False
        await db.commit()
        return True
    return False
