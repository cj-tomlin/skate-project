"""
Authentication helpers for tests.
"""

from datetime import timedelta
from typing import Dict, Any, Optional

from fastapi.testclient import TestClient

from app.domain.users.models.user import User
from app.infrastructure.security.jwt import create_access_token


def create_test_token(
    user_id: int,
    expires_delta: Optional[timedelta] = None,
    additional_data: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create a test JWT token for the given user_id.

    Args:
        user_id: The user ID to include in the token
        expires_delta: Optional expiration time delta
        additional_data: Additional claims to include in the token

    Returns:
        A JWT token string
    """
    data = {"sub": str(user_id)}
    if additional_data:
        data.update(additional_data)

    return create_access_token(
        data=data, expires_delta=expires_delta or timedelta(minutes=30)
    )


def authenticate_client(client: TestClient, user: User) -> TestClient:
    """
    Authenticate a test client with the given user.

    Args:
        client: The TestClient instance
        user: The user to authenticate as

    Returns:
        The authenticated TestClient
    """
    token = create_test_token(user.id)
    client.headers = {"Authorization": f"Bearer {token}"}
    return client


class AuthenticatedClient:
    """
    Context manager for authenticated API requests.

    Usage:
        with AuthenticatedClient(client, user) as auth_client:
            response = auth_client.get("/api/v1/users/users/me")
    """

    def __init__(self, client: TestClient, user: User):
        self.client = client
        self.user = user
        self.original_headers = client.headers.copy()

    def __enter__(self) -> TestClient:
        """Set up authentication headers."""
        token = create_test_token(self.user.id)
        self.client.headers = {
            **self.client.headers,
            "Authorization": f"Bearer {token}",
        }
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore original headers."""
        self.client.headers = self.original_headers
