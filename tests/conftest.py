import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models.base import Base

# Replace with your actual test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://skate_test_user:skate_test_password@localhost:5433/skate_test_db"
# Let pytest-asyncio handle the event loop


@pytest_asyncio.fixture(scope="function")
async def db_engine():
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
async def db_session(db_engine):
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
