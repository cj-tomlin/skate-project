from authlib.jose import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from passlib.context import CryptContext
import config

SECRET_KEY = config.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# JWT creation
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    header = {"alg": ALGORITHM}
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(header, to_encode, SECRET_KEY)
    return encoded_jwt


# JWT decoding
def decode_access_token(token: str):
    try:
        decoded_jwt = jwt.decode(token, SECRET_KEY)
        return decoded_jwt
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
