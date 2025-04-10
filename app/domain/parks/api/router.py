"""
Router for parks domain.
"""

from fastapi import APIRouter

from app.domain.parks.api.park_router import router as park_router
from app.domain.parks.api.feature_router import router as feature_router


# Create the main router for the parks domain
router = APIRouter()

# Include the park and feature routers
router.include_router(park_router, prefix="/parks")
router.include_router(feature_router, prefix="/features")
