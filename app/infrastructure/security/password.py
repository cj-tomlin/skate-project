from passlib.context import CryptContext
from fastapi import HTTPException, status
from typing import Optional

# Configure password hashing
pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=12, deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: The plain text password to hash

    Returns:
        The hashed password

    Raises:
        ValueError: If the password is empty
    """
    if not password:
        raise ValueError("Password cannot be empty.")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to verify against

    Returns:
        True if the password matches, False otherwise

    Raises:
        HTTPException: If there's an error during verification
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password."
        )


def verify_and_update_password(
    plain_password: str, hashed_password: str
) -> tuple[bool, Optional[str]]:
    """
    Verify a password against a hash and update the hash if needed.

    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to verify against

    Returns:
        A tuple of (is_verified, new_hash_if_needed)

    Raises:
        HTTPException: If there's an error during verification
    """
    try:
        is_verified = pwd_context.verify(plain_password, hashed_password)
        # Check if the hash needs to be updated
        new_hash = None
        if is_verified and pwd_context.needs_update(hashed_password):
            new_hash = hash_password(plain_password)
        return is_verified, new_hash
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password."
        )
