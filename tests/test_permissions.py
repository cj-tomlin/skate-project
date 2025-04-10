import pytest
from fastapi import HTTPException, status
from unittest.mock import patch
from app.services.permissions import require_role
from app.models.user import Role, User


class TestPermissions:
    def test_require_role_matching_role(self):
        """Test that require_role allows access when roles match."""
        # Setup
        user = User(
            id=1,
            username="admin",
            email="admin@example.com",
            hashed_password="hashed_password",
            role=Role.ADMIN,
            is_active=True,
        )
        role_checker = require_role(Role.ADMIN)

        # Execute & Assert
        # If roles match, the function should return the user without raising an exception
        assert role_checker(user) == user

    def test_require_role_non_matching_role(self):
        """Test that require_role denies access when roles don't match."""
        # Setup
        user = User(
            id=1,
            username="user",
            email="user@example.com",
            hashed_password="hashed_password",
            role=Role.USER,
            is_active=True,
        )
        role_checker = require_role(Role.ADMIN)

        # Execute & Assert
        # If roles don't match, the function should raise an HTTPException
        with pytest.raises(HTTPException) as excinfo:
            role_checker(user)
        assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Insufficient permissions" in str(excinfo.value.detail)

    def test_require_role_moderator(self):
        """Test that require_role works with moderator role."""
        # Setup
        user = User(
            id=1,
            username="mod",
            email="mod@example.com",
            hashed_password="hashed_password",
            role=Role.MODERATOR,
            is_active=True,
        )
        role_checker = require_role(Role.MODERATOR)

        # Execute & Assert
        assert role_checker(user) == user

    @patch("app.services.permissions.get_current_user")
    def test_require_role_as_dependency(self, mock_get_current_user):
        """Test require_role when used as a dependency."""
        # Setup
        admin_user = User(
            id=1,
            username="admin",
            email="admin@example.com",
            hashed_password="hashed_password",
            role=Role.ADMIN,
            is_active=True,
        )
        mock_get_current_user.return_value = admin_user

        # Create the role checker for the same role as the user
        role_checker = require_role(Role.ADMIN)

        # Mock the Depends function to directly return the user
        with patch(
            "app.services.permissions.Depends", side_effect=lambda x: admin_user
        ):
            # Execute
            result = role_checker(admin_user)

            # Assert
            assert result == admin_user
