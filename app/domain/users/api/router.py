from fastapi import APIRouter

from app.domain.users.api.user_router import router as user_router
from app.domain.users.api.auth_router import router as auth_router


# Create the main router for the users domain
router = APIRouter()

# Include the user and auth routers
router.include_router(user_router, prefix="/users")
router.include_router(auth_router, prefix="/auth", tags=["auth"])
