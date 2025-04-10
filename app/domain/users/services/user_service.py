from typing import Optional, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.users.models.user import User
from app.domain.users.repositories.user_repository import UserRepository
from app.domain.users.schemas.user import UserCreate, UserUpdate
from app.infrastructure.security.password import hash_password, verify_password
from app.core.exceptions import NotFoundError, ValidationError, AuthenticationError


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    Get a user by ID.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        The user if found, None otherwise
    """
    repo = UserRepository(db)
    return await repo.get_by_id(user_id)


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """
    Get a user by username.

    Args:
        db: Database session
        username: Username

    Returns:
        The user if found, None otherwise
    """
    repo = UserRepository(db)
    return await repo.get_by_username(username)


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    Get a user by email.

    Args:
        db: Database session
        email: Email address

    Returns:
        The user if found, None otherwise
    """
    repo = UserRepository(db)
    return await repo.get_by_email(email)


async def get_user_by_username_or_email(
    db: AsyncSession, username_or_email: str
) -> Optional[User]:
    """
    Get a user by username or email.

    Args:
        db: Database session
        username_or_email: Username or email

    Returns:
        The user if found, None otherwise
    """
    repo = UserRepository(db)
    return await repo.get_by_username_or_email(username_or_email)


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    """
    Create a new user.

    Args:
        db: Database session
        user_data: User creation data

    Returns:
        The created user

    Raises:
        ValidationError: If username or email already exists
    """
    repo = UserRepository(db)

    # Check if username already exists
    existing_user = await repo.get_by_username(user_data.username)
    if existing_user:
        raise ValidationError(f"Username '{user_data.username}' already exists")

    # Check if email already exists
    existing_user = await repo.get_by_email(user_data.email)
    if existing_user:
        raise ValidationError(f"Email '{user_data.email}' already exists")

    # Hash the password
    hashed_password = hash_password(user_data.password)

    # Create user data dictionary
    user_dict = user_data.model_dump(exclude={"password"})
    user_dict["hashed_password"] = hashed_password

    # Create the user
    return await repo.create(user_dict)


async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate) -> User:
    """
    Update a user.

    Args:
        db: Database session
        user_id: User ID
        user_data: User update data

    Returns:
        The updated user

    Raises:
        NotFoundError: If the user is not found
        ValidationError: If username or email already exists
    """
    repo = UserRepository(db)

    # Check if user exists
    user = await repo.get_by_id(user_id)
    if not user:
        raise NotFoundError(f"User with ID {user_id} not found")

    # Check if username already exists (if being updated)
    if user_data.username and user_data.username != user.username:
        existing_user = await repo.get_by_username(user_data.username)
        if existing_user:
            raise ValidationError(f"Username '{user_data.username}' already exists")

    # Check if email already exists (if being updated)
    if user_data.email and user_data.email != user.email:
        existing_user = await repo.get_by_email(user_data.email)
        if existing_user:
            raise ValidationError(f"Email '{user_data.email}' already exists")

    # Update the user
    user_dict = user_data.model_dump(exclude_unset=True)
    updated_user = await repo.update(user_id, user_dict)

    return updated_user


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    """
    Soft delete a user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        True if the user was deleted, False otherwise

    Raises:
        NotFoundError: If the user is not found
    """
    repo = UserRepository(db)

    # Check if user exists
    user = await repo.get_by_id(user_id)
    if not user:
        raise NotFoundError(f"User with ID {user_id} not found")

    # Delete the user
    return await repo.delete(user_id)


async def undelete_user(db: AsyncSession, user_id: int) -> bool:
    """
    Undelete a soft-deleted user.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        True if the user was undeleted, False otherwise

    Raises:
        NotFoundError: If the user is not found
    """
    repo = UserRepository(db)

    # Check if user exists
    user = await repo.get_by_id(user_id)
    if not user:
        raise NotFoundError(f"User with ID {user_id} not found")

    # Undelete the user
    return await repo.undelete(user_id)


async def change_password(
    db: AsyncSession, user_id: int, old_password: str, new_password: str
) -> bool:
    """
    Change a user's password.

    Args:
        db: Database session
        user_id: User ID
        old_password: Current password
        new_password: New password

    Returns:
        True if the password was changed, False otherwise

    Raises:
        NotFoundError: If the user is not found
        AuthenticationError: If the old password is incorrect
    """
    repo = UserRepository(db)

    # Check if user exists
    user = await repo.get_by_id(user_id)
    if not user:
        raise NotFoundError(f"User with ID {user_id} not found")

    # Verify old password
    if not verify_password(old_password, user.hashed_password):
        raise AuthenticationError("Incorrect password")

    # Hash new password
    hashed_password = hash_password(new_password)

    # Update password
    await repo.update(user_id, {"hashed_password": hashed_password})

    return True


async def activate_user(db: AsyncSession, user_id: int) -> bool:
    """
    Activate a user account.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        True if the user was activated, False otherwise

    Raises:
        NotFoundError: If the user is not found
    """
    repo = UserRepository(db)

    # Check if user exists
    user = await repo.get_by_id(user_id)
    if not user:
        raise NotFoundError(f"User with ID {user_id} not found")

    # Check if already active
    if user.is_active:
        return False

    # Activate the user
    await repo.update(user_id, {"is_active": True})

    return True


async def deactivate_user(db: AsyncSession, user_id: int) -> bool:
    """
    Deactivate a user account.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        True if the user was deactivated, False otherwise

    Raises:
        NotFoundError: If the user is not found
    """
    repo = UserRepository(db)

    # Check if user exists
    user = await repo.get_by_id(user_id)
    if not user:
        raise NotFoundError(f"User with ID {user_id} not found")

    # Check if already inactive
    if not user.is_active:
        return False

    # Deactivate the user
    await repo.update(user_id, {"is_active": False})

    return True


async def list_users(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> Tuple[List[User], int]:
    """
    List users with pagination.

    Args:
        db: Database session
        skip: Number of users to skip
        limit: Maximum number of users to return

    Returns:
        Tuple of (list of users, total count)
    """
    repo = UserRepository(db)

    # Get users
    users = await repo.list(skip=skip, limit=limit)

    # Get total count
    total = await repo.count()

    return users, total


async def update_last_login(db: AsyncSession, user_id: int) -> bool:
    """
    Update a user's last login timestamp.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        True if the timestamp was updated, False otherwise
    """
    repo = UserRepository(db)

    # Check if user exists
    user = await repo.get_by_id(user_id)
    if not user:
        return False

    # Update last login timestamp
    user.update_last_login()
    await db.flush()

    return True
