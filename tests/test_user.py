import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
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
from app.models.user import Base
from app.schemas.user import UserCreate, UserUpdate

# Set up a test database
engine = create_engine("sqlite:///:memory:")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def unique_user_data():
    """Generate unique user data for each test to avoid conflicts."""
    return UserCreate(
        username="testuser",
        email="unique_test@example.com",
        password="password123",
        role="user",
        bio="Sample bio",
        profile_picture_url=None,
    )


# Add a fixture for rollback
@pytest.fixture(autouse=True)
def rollback_session(test_db):
    """Rollback the session after each test to reset the database state."""
    yield
    test_db.rollback()


def test_create_user(test_db, unique_user_data):
    user = create_user(test_db, unique_user_data)
    assert user.id is not None
    assert user.email == unique_user_data.email


def test_get_user_by_id(test_db, unique_user_data):
    user = create_user(test_db, unique_user_data)
    retrieved_user = get_user_by_id(test_db, user.id)
    assert retrieved_user is not None
    assert retrieved_user.email == unique_user_data.email


def test_update_user(test_db, unique_user_data):
    user = create_user(test_db, unique_user_data)
    update_data = UserUpdate(bio="Updated bio")
    updated_user = update_user(test_db, user.id, update_data)
    assert updated_user.bio == "Updated bio"


def test_delete_and_undelete_user(test_db, unique_user_data):
    user = create_user(test_db, unique_user_data)
    assert delete_user(test_db, user.id)
    assert get_user_by_id(test_db, user.id).deleted_at is not None

    assert undelete_user(test_db, user.id)
    assert get_user_by_id(test_db, user.id).deleted_at is None


def test_update_last_login(test_db, unique_user_data):
    user = create_user(test_db, unique_user_data)
    assert update_last_login(test_db, user.id)
    assert get_user_by_id(test_db, user.id).last_login is not None


def test_change_password(test_db, unique_user_data):
    user = create_user(test_db, unique_user_data)
    assert change_password(test_db, user.id, "password123", "newpassword456")
    assert not change_password(test_db, user.id, "wrongpassword", "newpassword456")


def test_activate_and_deactivate_user(test_db, unique_user_data):
    user = create_user(test_db, unique_user_data)
    deactivate_user(test_db, user.id)
    assert get_user_by_id(test_db, user.id).is_active is False

    activate_user(test_db, user.id)
    assert get_user_by_id(test_db, user.id).is_active is True
