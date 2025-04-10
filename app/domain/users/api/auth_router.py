from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.users.schemas.auth import (
    Token,
    LoginRequest,
    LoginResponse,
)
from app.domain.users.services.auth_service import login_user
from app.infrastructure.database.session import get_db_session
from app.core.exceptions import AuthenticationError


router = APIRouter()


@router.post(
    "/token",
    response_model=Token,
    summary="Get access token",
    description="OAuth2 compatible token login, get an access token for future requests.",
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db_session),
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    try:
        user, access_token, expires_in = await login_user(
            db, form_data.username, form_data.password
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": expires_in,
        }
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Login",
    description="Login with username/email and password, get an access token and user information.",
)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Login with username/email and password.
    Returns an access token and user information.
    """
    try:
        user, access_token, expires_in = await login_user(
            db, login_data.username, login_data.password
        )
        return {
            "token": {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": expires_in,
            },
            "user": user,
        }
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
