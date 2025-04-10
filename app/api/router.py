from fastapi import APIRouter
from app.api.v1 import router as v1_router

# Create the main API router
router = APIRouter()

# Include API version routers
router.include_router(v1_router, prefix="/v1")

# Add more API versions as needed
# Example:
# from app.api.v2 import router as v2_router
# router.include_router(v2_router, prefix="/v2")
