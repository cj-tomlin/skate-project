from pydantic import BaseModel, EmailStr, Field, HttpUrl, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

from app.domain.users.models.user import Role


# Base schema for general user information
class UserBase(BaseModel):
    """
    Base schema for user information.
    Contains fields common to all user-related schemas.
    """

    username: str = Field(
        ..., min_length=3, max_length=50, description="User's unique username"
    )
    email: EmailStr = Field(..., description="User's email address")
    role: Role = Field(default=Role.USER, description="User's role")
    bio: Optional[str] = Field(None, max_length=500, description="User's bio text")
    profile_picture_url: Optional[HttpUrl] = Field(
        None, description="URL to user's profile picture"
    )


# Schema for creating a user, with password
class UserCreate(UserBase):
    """
    Schema for creating a new user.
    Extends UserBase with password field.
    """

    password: str = Field(
        ..., min_length=8, description="Password for user account creation"
    )


# Schema for updating a user
class UserUpdate(BaseModel):
    """
    Schema for updating an existing user.
    All fields are optional to allow partial updates.
    """

    username: Optional[str] = Field(
        None, min_length=3, max_length=50, description="Updated username"
    )
    email: Optional[EmailStr] = Field(None, description="Updated email address")
    bio: Optional[str] = Field(None, max_length=500, description="Updated bio text")
    profile_picture_url: Optional[HttpUrl] = Field(
        None, description="Updated URL to user's profile picture"
    )
    is_active: Optional[bool] = Field(
        None, description="Indicates if the user is active"
    )
    role: Optional[Role] = Field(None, description="Updated user role")
    two_factor_enabled: Optional[bool] = Field(
        None, description="Two-factor authentication enabled"
    )
    settings: Optional[Dict[str, Any]] = Field(
        None, description="User-specific settings/preferences"
    )

    model_config = ConfigDict(
        extra="forbid",  # Forbid extra fields to prevent typos
    )


# Schema for changing password
class PasswordChange(BaseModel):
    """Schema for changing a user's password."""

    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")


# Detailed schema for user response
class UserResponse(UserBase):
    """
    Schema for user response data.
    Extends UserBase with additional user details.
    """

    id: int = Field(..., description="Unique user ID")
    is_active: bool = Field(..., description="Indicates if the user is active")
    is_verified: bool = Field(..., description="Indicates if the user is verified")
    two_factor_enabled: bool = Field(
        ..., description="Two-factor authentication enabled"
    )
    created_at: datetime = Field(..., description="User account creation timestamp")
    updated_at: datetime = Field(
        ..., description="Timestamp for last user profile update"
    )
    last_login_at: Optional[datetime] = Field(
        None, description="Timestamp for last user login"
    )
    deleted_at: Optional[datetime] = Field(
        None, description="Timestamp for account deletion, if applicable"
    )
    settings: Optional[Dict[str, Any]] = Field(
        None, description="User-specific settings/preferences"
    )

    model_config = ConfigDict(
        from_attributes=True,  # Allow conversion from ORM model
    )


# Schema for user list response with pagination
class UserListResponse(BaseModel):
    """Schema for paginated list of users."""

    items: list[UserResponse]
    total: int
    page: int
    page_size: int
    pages: int
