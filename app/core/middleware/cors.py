from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.core.config import settings


def setup_cors_middleware(app: FastAPI) -> None:
    """
    Set up CORS middleware for the FastAPI application.

    Args:
        app: The FastAPI application instance
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=settings.CORS_METHODS,
        allow_headers=settings.CORS_HEADERS,
    )
