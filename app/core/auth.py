from authlib.jose import jwt, JoseError
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from passlib.context import CryptContext
from app.core import config

SECRET_KEY = config.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# JWT creation
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    header = {"alg": ALGORITHM}
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})

    # Encode the JWT and return as a string
    encoded_jwt = jwt.encode(header, to_encode, SECRET_KEY).decode("utf-8")
    return encoded_jwt


# JWT decoding with manual expiration check
def decode_access_token(token: str):
    try:
        decoded_jwt = jwt.decode(token, SECRET_KEY)

        # Manually check if the token has expired
        if "exp" in decoded_jwt:
            exp_timestamp = decoded_jwt["exp"]
            exp = datetime.fromtimestamp(
                exp_timestamp, tz=timezone.utc
            )  # Convert timestamp to datetime
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
