from fastapi import HTTPException, status
from typing import Any, Dict, Optional


class AppException(HTTPException):
    """
    Base exception for application-specific exceptions.
    Extends FastAPI's HTTPException with additional fields.
    """

    def __init__(
        self,
        status_code: int,
        detail: str,
        code: str = "error",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.code = code


class NotFoundError(AppException):
    """Exception raised when a resource is not found."""

    def __init__(
        self,
        detail: str = "Resource not found",
        code: str = "not_found",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            code=code,
            headers=headers,
        )


class ValidationError(AppException):
    """Exception raised when validation fails."""

    def __init__(
        self,
        detail: str = "Validation error",
        code: str = "validation_error",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            code=code,
            headers=headers,
        )


class AuthenticationError(AppException):
    """Exception raised when authentication fails."""

    def __init__(
        self,
        detail: str = "Authentication failed",
        code: str = "authentication_error",
        headers: Optional[Dict[str, Any]] = None,
    ):
        if headers is None:
            headers = {"WWW-Authenticate": "Bearer"}
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            code=code,
            headers=headers,
        )


class AuthorizationError(AppException):
    """Exception raised when authorization fails."""

    def __init__(
        self,
        detail: str = "Insufficient permissions",
        code: str = "authorization_error",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            code=code,
            headers=headers,
        )


class DatabaseError(AppException):
    """Exception raised when a database operation fails."""

    def __init__(
        self,
        detail: str = "Database error",
        code: str = "database_error",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            code=code,
            headers=headers,
        )
