"""
Mock helpers for tests.
"""

import contextlib
from typing import Any, Dict, Generator, Optional, Type, Callable
from unittest.mock import MagicMock, patch


class MockResponse:
    """
    Mock HTTP response for testing external API calls.

    Attributes:
        status_code: HTTP status code
        json_data: Data to return from json() method
        text: Response text
        content: Response content as bytes
        headers: Response headers
        raise_for_status: Function to call for raise_for_status method
    """

    def __init__(
        self,
        status_code: int = 200,
        json_data: Optional[Dict[str, Any]] = None,
        text: str = "",
        content: bytes = b"",
        headers: Optional[Dict[str, str]] = None,
        raise_for_status: Optional[Callable[[], None]] = None,
    ):
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text
        self.content = content
        self.headers = headers or {}
        self._raise_for_status = raise_for_status

    def json(self) -> Dict[str, Any]:
        """Return JSON data."""
        return self._json_data

    def raise_for_status(self) -> None:
        """Raise an exception if status code indicates an error."""
        if self._raise_for_status:
            self._raise_for_status()


@contextlib.contextmanager
def mock_external_api(
    module_path: str,
    method_name: str,
    return_value: Any = None,
    side_effect: Any = None,
) -> Generator[MagicMock, None, None]:
    """
    Context manager for mocking external API calls.

    Args:
        module_path: Path to the module containing the method to mock
        method_name: Name of the method to mock
        return_value: Value to return from the mocked method
        side_effect: Side effect for the mocked method

    Yields:
        The mock object

    Usage:
        with mock_external_api("app.services.external", "fetch_data",
                              return_value={"data": "mocked"}) as mock:
            result = service.get_external_data()
            assert result == {"data": "mocked"}
            mock.assert_called_once()
    """
    target = f"{module_path}.{method_name}"
    with patch(target) as mock:
        if return_value is not None:
            mock.return_value = return_value
        if side_effect is not None:
            mock.side_effect = side_effect
        yield mock


def create_mock_repository(repository_class: Type[Any]) -> MagicMock:
    """
    Create a mock repository with all methods mocked.

    Args:
        repository_class: The repository class to mock

    Returns:
        A mock repository instance
    """
    mock_repo = MagicMock(spec=repository_class)

    # Common repository methods to mock
    mock_repo.get_by_id.return_value = None
    mock_repo.get_all.return_value = []
    mock_repo.create.return_value = None
    mock_repo.update.return_value = None
    mock_repo.delete.return_value = None

    return mock_repo


@contextlib.contextmanager
def mock_dependency(
    app, dependency_name: str, mock_value: Any
) -> Generator[None, None, None]:
    """
    Context manager for mocking FastAPI dependencies.

    Args:
        app: FastAPI application instance
        dependency_name: Name of the dependency to mock
        mock_value: Value to use for the dependency

    Yields:
        None

    Usage:
        with mock_dependency(app, "get_current_user", mock_user):
            response = client.get("/api/v1/users/users/me")
            assert response.status_code == 200
    """
    original_dependencies = app.dependency_overrides.copy()
    try:
        app.dependency_overrides[dependency_name] = lambda: mock_value
        yield
    finally:
        app.dependency_overrides = original_dependencies
