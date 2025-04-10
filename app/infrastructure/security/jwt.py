from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from authlib.jose import jwt, JoseError
from fastapi import HTTPException, status
from app.core.config import settings

# JWT settings
ALGORITHM = "HS256"


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token.

    Args:
        data: The data to encode in the token
        expires_delta: Optional expiration time delta, defaults to 30 minutes

    Returns:
        The encoded JWT token as a string
    """
    header = {"alg": ALGORITHM}
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(header, to_encode, settings.SECRET_KEY).decode("utf-8")


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT access token.

    Args:
        token: The JWT token to decode

    Returns:
        The decoded token payload

    Raises:
        HTTPException: If the token is invalid or expired
    """
    try:
        decoded_jwt = jwt.decode(token, settings.SECRET_KEY)
        exp_timestamp = decoded_jwt.get("exp")

        if exp_timestamp and isinstance(exp_timestamp, (int, float)):
            exp = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            if datetime.now(timezone.utc) > exp:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                )
        elif exp_timestamp is not None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token expiration",
            )

        return decoded_jwt
    except JoseError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
