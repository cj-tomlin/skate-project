from fastapi import Depends, HTTPException, status
from app.models.user import Role, User
from app.dependencies.auth import get_current_user


def require_role(role: Role):
    """Dependency generator for role-based access control."""

    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return current_user

    return role_checker
