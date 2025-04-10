from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Enum as SqlAlchemyEnum,
    DateTime,
)
from sqlalchemy.dialects.postgresql import JSON
from enum import Enum
from datetime import datetime, timezone

from app.infrastructure.database.base import Base


class Role(str, Enum):
    """User roles for role-based access control."""

    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    # Commented out roles can be uncommented when needed
    # GUEST = "guest"
    # PREMIUM_USER = "premium_user"
    # CONTENT_CREATOR = "content_creator"


class User(Base):
    """
    User model representing application users.

    Attributes:
        id: Unique identifier for the user
        username: Unique username for the user
        email: Unique email address for the user
        hashed_password: Hashed password for authentication
        is_active: Whether the user account is active
        role: The user's role for access control
        is_verified: Whether the user's email has been verified
        two_factor_enabled: Whether two-factor authentication is enabled
        created_at: When the user account was created
        updated_at: When the user account was last updated
        last_login_at: When the user last logged in
        deleted_at: When the user was soft-deleted (if applicable)
        profile_picture_url: URL to the user's profile picture
        bio: User's biography or description
        settings: User-specific settings stored as JSON
    """

    __tablename__ = "users"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Identification and Authentication
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # Account Status and Permissions
    is_active = Column(Boolean, default=True)
    role = Column(SqlAlchemyEnum(Role), default=Role.USER)
    is_verified = Column(Boolean, default=False)
    two_factor_enabled = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Profile Information
    profile_picture_url = Column(String(255), nullable=True)
    bio = Column(String(500), nullable=True)
    settings = Column(JSON, nullable=True)

    def __repr__(self):
        return (
            f"<User(id={self.id}, username='{self.username}', "
            f"email='{self.email}', role='{self.role}', is_active={self.is_active})>"
        )

    def soft_delete(self):
        """Set the user as deleted by populating deleted_at."""
        self.deleted_at = datetime.now(timezone.utc)

    def undelete(self):
        """Restore a soft-deleted user by clearing deleted_at."""
        self.deleted_at = None

    @property
    def is_deleted(self):
        """Check if the user is soft-deleted."""
        return self.deleted_at is not None

    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login_at = datetime.now(timezone.utc)

    def activate(self):
        """Activate the user account."""
        self.is_active = True

    def deactivate(self):
        """Deactivate the user account."""
        self.is_active = False

    def verify(self):
        """Mark the user as verified."""
        self.is_verified = True

    def enable_two_factor(self):
        """Enable two-factor authentication."""
        self.two_factor_enabled = True

    def disable_two_factor(self):
        """Disable two-factor authentication."""
        self.two_factor_enabled = False
