from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.users.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    PasswordChange,
)
from app.domain.users.services import (
    create_user,
    get_user_by_id,
    update_user,
    delete_user,
    undelete_user,
    change_password,
    activate_user,
    deactivate_user,
    list_users,
)
from app.domain.users.models.user import Role
from app.infrastructure.database.session import get_db_session
from app.infrastructure.security.auth import (
    get_current_active_user,
    require_role,
)
from app.domain.users.models.user import User


router = APIRouter()


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Create a new user account. This endpoint is public and can be used for user registration.",
)
async def create_new_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db_session),
):
    """Create a new user."""
    user = await create_user(db, user_data)
    return user


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get the current authenticated user's information.",
)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
):
    """Retrieve the current user's information."""
    return current_user


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user by ID",
    description="Get a user by their ID. Requires moderator or admin role.",
)
async def get_user_info(
    user_id: int = Path(..., description="The ID of the user to retrieve"),
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role(Role.MODERATOR)),
):
    """Retrieve a user by ID."""
    user = await get_user_by_id(db, user_id)
    return user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user",
    description="Update the current authenticated user's information.",
)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Update the current user's information."""
    updated_user = await update_user(db, current_user.id, user_data)
    return updated_user


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user by ID",
    description="Update a user by their ID. Requires moderator or admin role.",
)
async def update_user_by_id(
    user_data: UserUpdate,
    user_id: int = Path(..., description="The ID of the user to update"),
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role(Role.MODERATOR)),
):
    """Update a user's information."""
    updated_user = await update_user(db, user_id, user_data)
    return updated_user


@router.put(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Change current user password",
    description="Change the current authenticated user's password.",
)
async def change_current_user_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Change the current user's password."""
    await change_password(
        db, current_user.id, password_data.old_password, password_data.new_password
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Soft delete a user by their ID. Requires admin role.",
)
async def delete_user_by_id(
    user_id: int = Path(..., description="The ID of the user to delete"),
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role(Role.ADMIN)),
):
    """Soft delete a user."""
    await delete_user(db, user_id)


@router.put(
    "/{user_id}/undelete",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Undelete user",
    description="Restore a soft-deleted user by their ID. Requires admin role.",
)
async def undelete_user_by_id(
    user_id: int = Path(..., description="The ID of the user to undelete"),
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role(Role.ADMIN)),
):
    """Undelete a soft-deleted user."""
    await undelete_user(db, user_id)


@router.put(
    "/{user_id}/activate",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Activate user",
    description="Activate a user account by their ID. Requires admin role.",
)
async def activate_user_by_id(
    user_id: int = Path(..., description="The ID of the user to activate"),
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role(Role.ADMIN)),
):
    """Activate a user account."""
    await activate_user(db, user_id)


@router.put(
    "/{user_id}/deactivate",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate user",
    description="Deactivate a user account by their ID. Requires admin role.",
)
async def deactivate_user_by_id(
    user_id: int = Path(..., description="The ID of the user to deactivate"),
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role(Role.ADMIN)),
):
    """Deactivate a user account."""
    await deactivate_user(db, user_id)


@router.get(
    "/",
    response_model=UserListResponse,
    summary="List users",
    description="List users with pagination. Requires moderator or admin role.",
)
async def list_all_users(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Page size"),
    db: AsyncSession = Depends(get_db_session),
    _: User = Depends(require_role(Role.MODERATOR)),
):
    """List users with pagination."""
    skip = (page - 1) * page_size
    users, total = await list_users(db, skip=skip, limit=page_size)

    # Calculate total pages
    pages = (total + page_size - 1) // page_size

    return {
        "items": users,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }
