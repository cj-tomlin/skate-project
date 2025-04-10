from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

from app.domain.users.schemas.user import UserResponse


class Token(BaseModel):
    """
    Schema for authentication token response.
    Contains the access token and token type.
    """

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class TokenData(BaseModel):
    """
    Schema for token payload data.
    Contains the user ID and optional scopes.
    """

    sub: str = Field(..., description="Subject (user ID)")
    scopes: list[str] = Field(default_factory=list, description="Token scopes")
    exp: Optional[int] = Field(None, description="Expiration timestamp")


class LoginRequest(BaseModel):
    """
    Schema for login request.
    Contains the username/email and password.
    """

    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")

    model_config = ConfigDict(
        extra="forbid",  # Forbid extra fields to prevent typos
    )


class LoginResponse(BaseModel):
    """
    Schema for login response.
    Contains the token and user information.
    """

    token: Token
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """
    Schema for refresh token request.
    Contains the refresh token.
    """

    refresh_token: str = Field(..., description="Refresh token")

    model_config = ConfigDict(
        extra="forbid",  # Forbid extra fields to prevent typos
    )
