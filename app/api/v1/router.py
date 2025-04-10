from fastapi import APIRouter

from app.domain.users.api.router import router as users_router
from app.domain.parks.api.router import router as parks_router

# Create the v1 router
router = APIRouter()

# Import and include domain routers
router.include_router(users_router, tags=["users"])
router.include_router(parks_router, tags=["parks"])


# Health check endpoint
@router.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint.
    Returns a simple message to confirm the API is running.
    """
    return {"status": "ok", "version": "1.0"}
