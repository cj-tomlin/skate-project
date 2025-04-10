from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.infrastructure.security.jwt import decode_access_token
from app.infrastructure.database.session import get_db_session
from app.models.user import User, Role

# OAuth2 scheme for token extraction from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db_session),
) -> User:
    """
    Dependency to get the current authenticated user.

    Args:
        token: The JWT token from the request
        db: The database session

    Returns:
        The authenticated user

    Raises:
        HTTPException: If authentication fails
    """
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

    # Import here to avoid circular imports
    from app.domain.users.services.user_service import get_user_by_id

    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Dependency to get the current active user.

    Args:
        current_user: The authenticated user

    Returns:
        The active authenticated user

    Raises:
        HTTPException: If the user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )
    return current_user


def require_role(required_role: Role):
    """
    Dependency generator for role-based access control.

    Args:
        required_role: The role required to access the endpoint

    Returns:
        A dependency function that checks if the user has the required role
    """

    def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return current_user

    return role_checker


def require_roles(required_roles: list[Role]):
    """
    Dependency generator for multiple role-based access control.

    Args:
        required_roles: The roles required to access the endpoint

    Returns:
        A dependency function that checks if the user has any of the required roles
    """

    def roles_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return current_user

    return roles_checker


# Commonly used dependencies
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
AdminUser = Annotated[User, Depends(require_role(Role.ADMIN))]
ModeratorUser = Annotated[User, Depends(require_role(Role.MODERATOR))]
StaffUser = Annotated[User, Depends(require_roles([Role.ADMIN, Role.MODERATOR]))]
