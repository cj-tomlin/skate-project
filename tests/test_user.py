import pytest
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
from app.schemas.user import UserCreate, UserUpdate
import uuid


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
