import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text
from app.db import get_db, get_redis, redis_client
import redis.asyncio as redis


@pytest.fixture
async def redis_key_cleanup():
    """Fixture to clean up test keys in Redis after each test."""
    yield
    await redis_client.delete("test_key")


@pytest.mark.asyncio
async def test_get_redis():
    redis_instance = await get_redis()
    assert isinstance(redis_instance, redis.Redis)


@pytest.mark.asyncio
async def test_postgresql_connection():
    """Test if a connection to the PostgreSQL database can be established."""
    async for session in get_db():
        try:
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1
        except SQLAlchemyError as e:
            pytest.fail(f"PostgreSQL connection test failed: {e}")


@pytest.mark.asyncio
async def test_redis_connection(redis_key_cleanup):
    """Test if a connection to the Redis database can be established."""
    try:
        await redis_client.set("test_key", "test_value")
        value = await redis_client.get("test_key")
        assert value == "test_value"
    except Exception as e:
        pytest.fail(f"Redis connection test failed: {e}")


@pytest.mark.asyncio
async def test_redis_connection_error_handling(monkeypatch):
    """Test Redis connection error handling by mocking a connection failure."""

    def mock_redis_connection_error(*args, **kwargs):
        raise ConnectionError("Mocked connection error")

    monkeypatch.setattr(redis_client, "get", mock_redis_connection_error)

    with pytest.raises(ConnectionError, match="Mocked connection error"):
        await redis_client.get("non_existent_key")


@pytest.mark.asyncio
async def test_postgresql_connection_error_handling(monkeypatch):
    """Test PostgreSQL connection error handling by mocking a connection failure."""

    def mock_session_execute_error(*args, **kwargs):
        raise SQLAlchemyError("Mocked SQLAlchemy connection error")

    async for session in get_db():
        monkeypatch.setattr(session, "execute", mock_session_execute_error)
        with pytest.raises(SQLAlchemyError, match="Mocked SQLAlchemy connection error"):
            await session.execute(text("SELECT 1"))
