from fastapi import APIRouter
from app.api.routes.debug import router as debug_router
from app.api.routes.user import router as user_router


router = APIRouter()

# Include all individual routers
router.include_router(debug_router, tags=["debug"])
router.include_router(user_router, prefix="/users", tags=["users"])
