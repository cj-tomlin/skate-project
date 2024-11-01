from datetime import datetime, timedelta, timezone
from authlib.jose import jwt, JoseError
from fastapi import HTTPException, status
from app.core import config

SECRET_KEY = config.SECRET_KEY
ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    header = {"alg": ALGORITHM}
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    return jwt.encode(header, to_encode, SECRET_KEY).decode("utf-8")


def decode_access_token(token: str) -> dict:
    try:
        decoded_jwt = jwt.decode(token, SECRET_KEY)
        if "exp" in decoded_jwt:
            exp_timestamp = decoded_jwt["exp"]
            exp = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            if datetime.now(timezone.utc) > exp:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                )
        return decoded_jwt
    except JoseError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
