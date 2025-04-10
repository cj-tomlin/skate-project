from datetime import timedelta
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.users.models.user import User
from app.domain.users.services.user_service import (
    get_user_by_username_or_email,
    update_last_login,
)
from app.infrastructure.security.password import verify_password
from app.infrastructure.security.jwt import create_access_token
from app.core.exceptions import AuthenticationError
from app.core.config import settings


async def authenticate_user(
    db: AsyncSession, username_or_email: str, password: str
) -> User:
    """
    Authenticate a user with username/email and password.

    Args:
        db: Database session
        username_or_email: Username or email
        password: Password

    Returns:
        The authenticated user

    Raises:
        AuthenticationError: If authentication fails
    """
    # Get user by username or email
    user = await get_user_by_username_or_email(db, username_or_email)
    if not user:
        raise AuthenticationError("Invalid username or password")

    # Check if user is active
    if not user.is_active:
        raise AuthenticationError("User account is inactive")

    # Check if user is deleted
    if user.deleted_at:
        raise AuthenticationError("User account has been deleted")

    # Verify password
    if not verify_password(password, user.hashed_password):
        raise AuthenticationError("Invalid username or password")

    # Update last login timestamp
    await update_last_login(db, user.id)

    return user


async def create_user_token(
    user: User, expires_delta: Optional[timedelta] = None
) -> Tuple[str, int]:
    """
    Create an access token for a user.

    Args:
        user: The user to create a token for
        expires_delta: Optional expiration time delta

    Returns:
        Tuple of (access token, expiration time in seconds)
    """
    # Set expiration time
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Create token data
    token_data = {
        "sub": str(user.id),
        "username": user.username,
        "email": user.email,
        "role": user.role.value,
    }

    # Create token
    access_token = create_access_token(token_data, expires_delta)

    # Return token and expiration time
    return access_token, int(expires_delta.total_seconds())


async def login_user(
    db: AsyncSession, username_or_email: str, password: str
) -> Tuple[User, str, int]:
    """
    Login a user and create an access token.

    Args:
        db: Database session
        username_or_email: Username or email
        password: Password

    Returns:
        Tuple of (user, access token, expiration time in seconds)

    Raises:
        AuthenticationError: If authentication fails
    """
    # Authenticate user
    user = await authenticate_user(db, username_or_email, password)

    # Create token
    access_token, expires_in = await create_user_token(user)

    return user, access_token, expires_in
