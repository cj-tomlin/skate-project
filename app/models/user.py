from .base import Base
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


class Role(str, Enum):
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    # GUEST = "guest"
    # PREMIUM_USER = "premium_user"
    # CONTENT_CREATOR = "content_creator"


class User(Base):
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
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
    last_login_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)

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
