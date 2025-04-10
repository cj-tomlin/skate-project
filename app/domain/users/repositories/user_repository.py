from typing import Optional, List, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import or_

from app.domain.users.models.user import User
from app.core.exceptions import NotFoundError


class UserRepository:
    """
    Repository for user data access operations.
    Implements the repository pattern to abstract database operations.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_data: Dict[str, Any]) -> User:
        """
        Create a new user.

        Args:
            user_data: Dictionary with user data

        Returns:
            The created user
        """
        user = User(**user_data)
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get a user by ID.

        Args:
            user_id: The user ID

        Returns:
            The user if found, None otherwise
        """
        result = await self.session.execute(select(User).filter(User.id == user_id))
        return result.scalars().first()

    async def get_by_id_or_404(self, user_id: int) -> User:
        """
        Get a user by ID or raise a 404 error.

        Args:
            user_id: The user ID

        Returns:
            The user

        Raises:
            NotFoundError: If the user is not found
        """
        user = await self.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"User with ID {user_id} not found")
        return user

    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.

        Args:
            username: The username

        Returns:
            The user if found, None otherwise
        """
        result = await self.session.execute(
            select(User).filter(User.username == username)
        )
        return result.scalars().first()

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email.

        Args:
            email: The email address

        Returns:
            The user if found, None otherwise
        """
        result = await self.session.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    async def get_by_username_or_email(self, username_or_email: str) -> Optional[User]:
        """
        Get a user by username or email.

        Args:
            username_or_email: The username or email

        Returns:
            The user if found, None otherwise
        """
        result = await self.session.execute(
            select(User).filter(
                or_(User.username == username_or_email, User.email == username_or_email)
            )
        )
        return result.scalars().first()

    async def list(
        self, skip: int = 0, limit: int = 100, include_deleted: bool = False
    ) -> List[User]:
        """
        List users with pagination.

        Args:
            skip: Number of users to skip
            limit: Maximum number of users to return
            include_deleted: Whether to include soft-deleted users

        Returns:
            List of users
        """
        query = select(User)
        if not include_deleted:
            query = query.filter(User.deleted_at.is_(None))

        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def count(self, include_deleted: bool = False) -> int:
        """
        Count users.

        Args:
            include_deleted: Whether to include soft-deleted users

        Returns:
            Number of users
        """
        query = select(func.count(User.id))
        if not include_deleted:
            query = query.filter(User.deleted_at.is_(None))

        result = await self.session.execute(query)
        return result.scalar()

    async def update(self, user_id: int, user_data: Dict[str, Any]) -> Optional[User]:
        """
        Update a user.

        Args:
            user_id: The user ID
            user_data: Dictionary with user data to update

        Returns:
            The updated user if found, None otherwise
        """
        user = await self.get_by_id(user_id)
        if not user:
            return None

        for key, value in user_data.items():
            setattr(user, key, value)

        await self.session.flush()
        return user

    async def delete(self, user_id: int) -> bool:
        """
        Soft delete a user.

        Args:
            user_id: The user ID

        Returns:
            True if the user was deleted, False if not found
        """
        user = await self.get_by_id(user_id)
        if not user:
            return False

        user.soft_delete()
        await self.session.flush()
        return True

    async def undelete(self, user_id: int) -> bool:
        """
        Undelete a soft-deleted user.

        Args:
            user_id: The user ID

        Returns:
            True if the user was undeleted, False if not found
        """
        user = await self.get_by_id(user_id)
        if not user:
            return False

        user.undelete()
        await self.session.flush()
        return True

    async def hard_delete(self, user_id: int) -> bool:
        """
        Hard delete a user (permanent deletion).

        Args:
            user_id: The user ID

        Returns:
            True if the user was deleted, False if not found
        """
        user = await self.get_by_id(user_id)
        if not user:
            return False

        await self.session.delete(user)
        await self.session.flush()
        return True
