import os
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator, Dict, Any
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import create_app
from app.infrastructure.database.base import Base
from app.domain.users.models.user import User, Role
from tests.factories.user_factory import UserFactory

# Replace with your actual test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://skate_test_user:skate_test_password@localhost:5433/skate_test_db"


# Test configuration
@pytest.fixture(scope="session")
def app_config() -> Dict[str, Any]:
    """Provide application configuration for tests."""
    return {
        "testing": True,
        "database_url": TEST_DATABASE_URL,
        "jwt_secret_key": "test_secret_key",
        "jwt_algorithm": "HS256",
        "jwt_expiration_minutes": 30,
    }


@pytest.fixture(scope="session")
def app() -> FastAPI:
    """Create a FastAPI test application."""
    # Set environment to testing
    os.environ["ENV"] = "testing"

    # Create the FastAPI application
    return create_app()


@pytest.fixture(scope="function")
def client(app: FastAPI) -> TestClient:
    """Create a FastAPI TestClient."""
    return TestClient(app)


@pytest_asyncio.fixture(scope="function")
async def db_engine() -> AsyncGenerator:
    """Create a new engine for each test."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        future=True,
        echo=True,
        isolation_level="AUTOCOMMIT",  # This helps avoid transaction conflicts
    )

    # Create tables
    async with engine.begin() as conn:
        try:
            # Drop all tables first to ensure a clean state
            await conn.run_sync(Base.metadata.drop_all)
            # Then create them again
            await conn.run_sync(Base.metadata.create_all)

            # Set timezone to UTC for this connection to avoid timezone issues
            await conn.execute(text("SET TIME ZONE 'UTC'"))
        except Exception as e:
            print(f"Error setting up database: {e}")
            raise

    yield engine

    # Clean up
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional scope around a series of operations."""
    import logging

    logger = logging.getLogger(__name__)

    # Create a new session factory using the engine
    TestingSessionLocal = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=True,
    )

    # Create a new session for each test
    async with TestingSessionLocal() as session:
        # Set timezone to UTC for this session to avoid timezone issues
        await session.execute(text("SET TIME ZONE 'UTC'"))

        logger.info(f"Session created: {session}")
        yield session
        # Roll back any changes
        await session.rollback()
        logger.info(f"Session rolled back: {session}")


@pytest.fixture(scope="function")
def user_factory(db_session: AsyncSession) -> Generator:
    """
    Factory for creating test users with customizable attributes.

    Usage:
        def test_something(user_factory):
            user = user_factory(username="testuser", role=Role.ADMIN)
            # Test with the user
    """
    # Set the session for the factory
    UserFactory._meta.sqlalchemy_session = db_session

    def _create_user(**kwargs) -> User:
        """Create a test user with the given attributes."""
        return UserFactory.create(**kwargs)

    yield _create_user

    # Clean up
    UserFactory._meta.sqlalchemy_session = None


@pytest.fixture(scope="function")
def admin_user(user_factory) -> User:
    """Create an admin user for testing."""
    return user_factory(role=Role.ADMIN, is_verified=True)


@pytest.fixture(scope="function")
def regular_user(user_factory) -> User:
    """Create a regular user for testing."""
    return user_factory(role=Role.USER, is_verified=True)


@pytest.fixture(scope="function")
def authenticated_client(client: TestClient, regular_user: User) -> TestClient:
    """Create an authenticated client for testing."""
    from tests.utils.auth_helpers import authenticate_client

    return authenticate_client(client, regular_user)


@pytest.fixture(scope="function")
def admin_client(client: TestClient, admin_user: User) -> TestClient:
    """Create an admin authenticated client for testing."""
    from tests.utils.auth_helpers import authenticate_client

    return authenticate_client(client, admin_user)
