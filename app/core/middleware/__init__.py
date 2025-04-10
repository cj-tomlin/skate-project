from app.core.middleware.cors import setup_cors_middleware
from app.core.middleware.logging import setup_logging_middleware


def setup_middleware(app):
    """
    Set up all middleware for the FastAPI application.

    Args:
        app: The FastAPI application instance
    """
    setup_cors_middleware(app)
    setup_logging_middleware(app)
