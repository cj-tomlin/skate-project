"""
Unit tests for the user service.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone

from app.domain.users.models.user import User, Role
from app.domain.users.services import user_service
from app.domain.users.repositories.user_repository import UserRepository
from app.infrastructure.security.password import hash_password


class TestUserService:
    """Test suite for UserService."""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        return MagicMock()

    @pytest.fixture
    def mock_user_repo(self, monkeypatch):
        """Create a mock user repository."""
        mock_repo = MagicMock(spec=UserRepository)
        # Patch the UserRepository constructor to return our mock
        monkeypatch.setattr(
            "app.domain.users.services.user_service.UserRepository",
            lambda db: mock_repo,
        )
        return mock_repo

    @pytest.fixture
    def sample_user(self):
        """Create a sample user for testing."""
        return User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password=hash_password("password123"),
            is_active=True,
            role=Role.USER,
            is_verified=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

    async def test_get_user_by_id(self, mock_db, mock_user_repo, sample_user):
        """Test getting a user by ID."""
        # Arrange
        mock_user_repo.get_by_id.return_value = sample_user

        # Act
        result = await user_service.get_user_by_id(mock_db, 1)

        # Assert
        assert result == sample_user
        mock_user_repo.get_by_id.assert_called_once_with(1)

    async def test_get_user_by_id_not_found(self, mock_db, mock_user_repo):
        """Test getting a non-existent user by ID."""
        # Arrange
        mock_user_repo.get_by_id.return_value = None

        # Act
        result = await user_service.get_user_by_id(mock_db, 999)

        # Assert
        assert result is None
        mock_user_repo.get_by_id.assert_called_once_with(999)

    async def test_get_user_by_email(self, mock_db, mock_user_repo, sample_user):
        """Test getting a user by email."""
        # Arrange
        mock_user_repo.get_by_email.return_value = sample_user

        # Act
        result = await user_service.get_user_by_email(mock_db, "test@example.com")

        # Assert
        assert result == sample_user
        mock_user_repo.get_by_email.assert_called_once_with("test@example.com")

    async def test_get_user_by_username(self, mock_db, mock_user_repo, sample_user):
        """Test getting a user by username."""
        # Arrange
        mock_user_repo.get_by_username.return_value = sample_user

        # Act
        result = await user_service.get_user_by_username(mock_db, "testuser")

        # Assert
        assert result == sample_user
        mock_user_repo.get_by_username.assert_called_once_with("testuser")

    async def test_create_user(self, mock_db, mock_user_repo, sample_user):
        """Test creating a new user."""
        # Arrange
        from app.domain.users.schemas.user import UserCreate

        user_data = UserCreate(
            username="newuser", email="new@example.com", password="newpassword123"
        )
        mock_user_repo.get_by_username.return_value = None
        mock_user_repo.get_by_email.return_value = None
        mock_user_repo.create.return_value = sample_user

        # Act
        with patch("app.domain.users.services.user_service.hash_password") as mock_hash:
            mock_hash.return_value = "hashed_password"
            result = await user_service.create_user(mock_db, user_data)

        # Assert
        assert result == sample_user
        mock_user_repo.create.assert_called_once()

    async def test_update_user(self, mock_db, mock_user_repo, sample_user):
        """Test updating a user."""
        # Arrange
        from app.domain.users.schemas.user import UserUpdate

        user_id = 1
        update_data = UserUpdate(username="updateduser", bio="Updated bio")
        mock_user_repo.get_by_id.return_value = sample_user
        mock_user_repo.get_by_username.return_value = None
        mock_user_repo.update.return_value = sample_user

        # Act
        result = await user_service.update_user(mock_db, user_id, update_data)

        # Assert
        assert result == sample_user
        mock_user_repo.get_by_id.assert_called_once_with(user_id)
        mock_user_repo.update.assert_called_once()

    async def test_delete_user(self, mock_db, mock_user_repo, sample_user):
        """Test deleting a user."""
        # Arrange
        user_id = 1
        mock_user_repo.get_by_id.return_value = sample_user
        mock_user_repo.delete.return_value = True

        # Act
        result = await user_service.delete_user(mock_db, user_id)

        # Assert
        assert result is True
        mock_user_repo.get_by_id.assert_called_once_with(user_id)
        mock_user_repo.delete.assert_called_once_with(user_id)

    async def test_change_password(self, mock_db, mock_user_repo, sample_user):
        """Test changing a user's password."""
        # Arrange
        user_id = 1
        old_password = "password123"
        new_password = "newpassword123"
        mock_user_repo.get_by_id.return_value = sample_user

        # Act
        with patch(
            "app.domain.users.services.user_service.verify_password"
        ) as mock_verify:
            mock_verify.return_value = True
            with patch(
                "app.domain.users.services.user_service.hash_password"
            ) as mock_hash:
                mock_hash.return_value = "new_hashed_password"
                result = await user_service.change_password(
                    mock_db, user_id, old_password, new_password
                )

        # Assert
        assert result is True
        mock_user_repo.get_by_id.assert_called_once_with(user_id)
        mock_user_repo.update.assert_called_once()
