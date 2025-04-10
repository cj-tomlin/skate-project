import os
import webbrowser
import logging

import uvicorn
from fastapi import FastAPI

from app.core import settings, register_exception_handlers, setup_middleware
from app.api import router as api_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("app")

###################################################################
## Initialize FastAPI application
###################################################################


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        The configured FastAPI application
    """
    # Create FastAPI app
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="A FastAPI backend for the Skate Project",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Set up middleware
    setup_middleware(app)

    # Register exception handlers
    register_exception_handlers(app)

    # Include API router
    app.include_router(api_router, prefix="/api")

    # Add startup and shutdown events
    @app.on_event("startup")
    async def startup_event():
        logger.info(f"Starting {settings.APP_NAME} in {settings.ENV} environment")

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info(f"Shutting down {settings.APP_NAME}")

    return app


# Create the application instance
app = create_app()

if __name__ == "__main__":
    print(f"CWD = {os.getcwd()}")
    webbrowser.open(f"http://{settings.HOSTNAME}:{settings.PORT}/docs")
    uvicorn.run(
        "app.main:app",
        host=settings.HOSTNAME,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
