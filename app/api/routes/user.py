from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies.db import get_db_session
from app.dependencies.auth import get_current_user
from app.dependencies.permissions import require_role
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.models.user import Role, User
from app.services.user import (
    create_user,
    get_user_by_id,
    update_user,
    delete_user,
    undelete_user,
    change_password,
    activate_user,
    deactivate_user,
)

router = APIRouter()


# Open endpoint for user registration
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_new_user(user_data: UserCreate, db: Session = Depends(get_db_session)):
    """Create a new user."""
    user = create_user(db, user_data)
    return user


# Route for users to access their own profile (e.g., /users/me)
@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Retrieve the current user's information."""
    return current_user


# Route for admins and moderators to retrieve any user's information
@router.get(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_role(Role.MODERATOR))],
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Retrieve a user by ID."""
    user = get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Route for users to update their own information
@router.put("/me", response_model=UserResponse)
def update_user_info(
    user_data: UserUpdate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Update the current user's information."""
    updated_user = update_user(db, current_user.id, user_data)
    return updated_user


# Route for admins or moderators to update any user's information
@router.put(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[Depends(require_role(Role.MODERATOR))],
)
def update_any_user_info(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Update a user's information."""
    user = update_user(db, user_id, user_data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# Route for users to change their own password
@router.put("/me/password", status_code=status.HTTP_204_NO_CONTENT)
def change_own_password(
    old_password: str,
    new_password: str,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Change the current user's password."""
    if not change_password(db, current_user.id, old_password, new_password):
        raise HTTPException(
            status_code=400, detail="Old password is incorrect or user not found"
        )


# Admin-only route for soft deleting a user
@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
def soft_delete_user(user_id: int, db: Session = Depends(get_db_session)):
    """Soft delete a user."""
    if not delete_user(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")


# Admin-only route for undeleting a user
@router.put(
    "/{user_id}/undelete",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
def undelete_user_account(user_id: int, db: Session = Depends(get_db_session)):
    """Undelete a soft-deleted user."""
    if not undelete_user(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")


# Admin-only route to activate a user
@router.put(
    "/{user_id}/activate",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
def activate_user_account(user_id: int, db: Session = Depends(get_db_session)):
    """Activate a user account."""
    if not activate_user(db, user_id):
        raise HTTPException(status_code=404, detail="User not found or already active")


# Admin-only route to deactivate a user
@router.put(
    "/{user_id}/deactivate",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(Role.ADMIN))],
)
def deactivate_user_account(user_id: int, db: Session = Depends(get_db_session)):
    """Deactivate a user account."""
    if not deactivate_user(db, user_id):
        raise HTTPException(
            status_code=404, detail="User not found or already inactive"
        )
