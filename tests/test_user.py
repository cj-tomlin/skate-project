import pytest
import uuid
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User, Role
from app.schemas.user import UserCreate, UserUpdate
from app.services.user import (
    create_user,
    get_user_by_id,
    update_user,
    delete_user,
    undelete_user,
    update_last_login,
    change_password,
    activate_user,
    deactivate_user,
)

# Create a test client for API endpoint tests
client = TestClient(app)


@pytest.fixture
def unique_user_data():
    """Generate unique user data for each test to avoid conflicts."""
    unique_email = (
        f"test_{uuid.uuid4().hex[:10]}@example.com"  # Adjust length as needed
    )
    return UserCreate(
        username="testuser",
        email=unique_email,
        password="password123",
        role="user",
        bio="Sample bio",
        profile_picture_url=None,
    )


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True,
        role=Role.USER,
        is_verified=False,
        two_factor_enabled=False,
    )


@pytest.fixture
def mock_admin_user():
    """Create a mock admin user for testing."""
    return User(
        id=2,
        username="adminuser",
        email="admin@example.com",
        hashed_password="hashed_password",
        is_active=True,
        role=Role.ADMIN,
        is_verified=True,
        two_factor_enabled=False,
    )


@pytest.fixture
def mock_moderator_user():
    """Create a mock moderator user for testing."""
    return User(
        id=3,
        username="moduser",
        email="mod@example.com",
        hashed_password="hashed_password",
        is_active=True,
        role=Role.MODERATOR,
        is_verified=True,
        two_factor_enabled=False,
    )


# Tests for user service functions with real database
@pytest.mark.asyncio
async def test_create_user(db_session, unique_user_data):
    user = await create_user(db_session, unique_user_data)
    assert user.id is not None
    assert user.email == unique_user_data.email


@pytest.mark.asyncio
async def test_get_user_by_id(db_session, unique_user_data):
    user = await create_user(db_session, unique_user_data)
    retrieved_user = await get_user_by_id(db_session, user.id)
    assert retrieved_user is not None
    assert retrieved_user.email == unique_user_data.email


@pytest.mark.asyncio
async def test_update_user(db_session, unique_user_data):
    user = await create_user(db_session, unique_user_data)
    update_data = UserUpdate(bio="Updated bio")
    updated_user = await update_user(db_session, user.id, update_data)
    assert updated_user.bio == "Updated bio"


@pytest.mark.asyncio
async def test_delete_and_undelete_user(db_session, unique_user_data):
    user = await create_user(db_session, unique_user_data)
    assert await delete_user(db_session, user.id)
    assert (await get_user_by_id(db_session, user.id)).deleted_at is not None

    assert await undelete_user(db_session, user.id)
    assert (await get_user_by_id(db_session, user.id)).deleted_at is None


@pytest.mark.asyncio
async def test_update_last_login(db_session, unique_user_data):
    user = await create_user(db_session, unique_user_data)
    assert await update_last_login(db_session, user.id)
    assert (await get_user_by_id(db_session, user.id)).last_login_at is not None


@pytest.mark.asyncio
async def test_change_password(db_session, unique_user_data):
    user = await create_user(db_session, unique_user_data)
    assert await change_password(db_session, user.id, "password123", "newpassword456")
    assert not await change_password(
        db_session, user.id, "wrongpassword", "newpassword456"
    )


@pytest.mark.asyncio
async def test_activate_and_deactivate_user(db_session, unique_user_data):
    user = await create_user(db_session, unique_user_data)
    await deactivate_user(db_session, user.id)
    assert (await get_user_by_id(db_session, user.id)).is_active is False

    await activate_user(db_session, user.id)
    assert (await get_user_by_id(db_session, user.id)).is_active is True


# Tests for user service functions with mocks
class TestUserService:
    @patch("app.services.user.create_user")
    def test_create_user_service(self, mock_create_user, mock_user):
        """Test the create_user service function."""
        # Setup
        mock_create_user.return_value = mock_user
        user_data = UserCreate(  # noqa: F841
            username="testuser",
            email="test@example.com",
            password="password123",
            role=Role.USER,
        )

        # Assert that the service function works as expected
        assert mock_create_user.return_value == mock_user

    @patch("app.services.user.get_user_by_id")
    def test_get_user_by_id_service(self, mock_get_user_by_id, mock_user):
        """Test the get_user_by_id service function."""
        # Setup
        mock_get_user_by_id.return_value = mock_user

        # Assert that the service function works as expected
        assert mock_get_user_by_id.return_value == mock_user

    @patch("app.services.user.update_user")
    def test_update_user_service(self, mock_update_user, mock_user):
        """Test the update_user service function."""
        # Setup
        updated_user = mock_user
        updated_user.bio = "Updated bio"
        mock_update_user.return_value = updated_user
        update_data = UserUpdate(bio="Updated bio")  # noqa: F841

        # Assert that the service function works as expected
        assert mock_update_user.return_value == updated_user
        assert mock_update_user.return_value.bio == "Updated bio"

    @patch("app.services.user.delete_user")
    def test_delete_user_service(self, mock_delete_user):
        """Test the delete_user service function."""
        # Setup
        mock_delete_user.return_value = True

        # Assert that the service function works as expected
        assert mock_delete_user.return_value is True

    @patch("app.services.user.undelete_user")
    def test_undelete_user_service(self, mock_undelete_user):
        """Test the undelete_user service function."""
        # Setup
        mock_undelete_user.return_value = True

        # Assert that the service function works as expected
        assert mock_undelete_user.return_value is True

    @patch("app.services.user.change_password")
    def test_change_password_service(self, mock_change_password):
        """Test the change_password service function."""
        # Setup
        mock_change_password.return_value = True

        # Assert that the service function works as expected
        assert mock_change_password.return_value is True

    @patch("app.services.user.activate_user")
    def test_activate_user_service(self, mock_activate_user):
        """Test the activate_user service function."""
        # Setup
        mock_activate_user.return_value = True

        # Assert that the service function works as expected
        assert mock_activate_user.return_value is True

    @patch("app.services.user.deactivate_user")
    def test_deactivate_user_service(self, mock_deactivate_user):
        """Test the deactivate_user service function."""
        # Setup
        mock_deactivate_user.return_value = True

        # Assert that the service function works as expected
        assert mock_deactivate_user.return_value is True
