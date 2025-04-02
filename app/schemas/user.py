from pydantic import BaseModel, EmailStr, Field, HttpUrl, ConfigDict
from typing import Optional
from enum import Enum
from datetime import datetime


# Define user roles matching the database Enum
class UserRole(str, Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    # GUEST = "guest"
    # PREMIUM_USER = "premium_user"
    # CONTENT_CREATOR = "content_creator"


# Base schema for general user information
class UserBase(BaseModel):
    username: str = Field(..., max_length=50, description="User's unique username")
    email: EmailStr = Field(..., max_length=50, description="User's email address")
    role: UserRole = Field(default=UserRole.USER, description="User's role")
    bio: Optional[str] = Field(None, max_length=500, description="User's bio text")
    profile_picture_url: Optional[HttpUrl] = Field(
        None, description="URL to user's profile picture"
    )


# Schema for creating a user, with password
class UserCreate(UserBase):
    password: str = Field(
        ..., min_length=8, description="Password for user account creation"
    )


# Schema for updating a user
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, max_length=50, description="Updated username")
    email: Optional[EmailStr] = Field(None, description="Updated email address")
    bio: Optional[str] = Field(None, max_length=500, description="Updated bio text")
    profile_picture_url: Optional[HttpUrl] = Field(
        None, description="Updated URL to user's profile picture"
    )
    is_active: Optional[bool] = Field(
        True, description="Indicates if the user is active"
    )
    role: Optional[UserRole] = Field(None, description="Updated user role")
    two_factor_enabled: Optional[bool] = Field(
        None, description="Two-factor authentication enabled"
    )


# Detailed schema for user response
class UserResponse(UserBase):
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
    settings: Optional[dict] = Field(
        None, description="User-specific settings/preferences"
    )

    model_config = ConfigDict(from_attributes=True)
