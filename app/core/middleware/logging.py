import time
import logging
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings

# Configure logger
logger = logging.getLogger("app.middleware")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging request information.
    Logs the method, path, status code, and processing time for each request.
    """

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Process the request
        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time

        # Log request details
        logger.info(
            f"{request.method} {request.url.path} {response.status_code} "
            f"Completed in {process_time:.4f}s"
        )

        return response


def setup_logging_middleware(app: FastAPI) -> None:
    """
    Set up request logging middleware for the FastAPI application.

    Args:
        app: The FastAPI application instance
    """
    if settings.ENV != "testing":  # Skip in testing environment
        app.add_middleware(RequestLoggingMiddleware)
