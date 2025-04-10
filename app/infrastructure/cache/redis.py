import redis.asyncio as redis
from typing import AsyncGenerator
from app.core.config import settings


# Create Redis client
redis_client = redis.from_url(str(settings.REDIS_URL), decode_responses=True)


async def get_redis_client() -> AsyncGenerator[redis.Redis, None]:
    """
    Dependency for Redis client.
    Yields a Redis client that can be used for caching and other Redis operations.
    """
    try:
        yield redis_client
    except Exception as e:
        # Handle Redis connection error
        raise ConnectionError(f"Could not connect to Redis: {e}")


class RedisCache:
    """
    Redis cache implementation.
    Provides methods for working with Redis as a cache.
    """

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def get(self, key: str) -> str:
        """Get a value from the cache."""
        return await self.redis.get(key)

    async def set(self, key: str, value: str, expire: int = 0) -> bool:
        """Set a value in the cache with optional expiration in seconds."""
        return await self.redis.set(key, value, ex=expire if expire > 0 else None)

    async def delete(self, key: str) -> int:
        """Delete a value from the cache."""
        return await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if a key exists in the cache."""
        return await self.redis.exists(key) > 0

    async def ttl(self, key: str) -> int:
        """Get the time to live for a key in seconds."""
        return await self.redis.ttl(key)

    async def incr(self, key: str, amount: int = 1) -> int:
        """Increment a value in the cache."""
        return await self.redis.incr(key, amount)

    async def decr(self, key: str, amount: int = 1) -> int:
        """Decrement a value in the cache."""
        return await self.redis.decr(key, amount)


async def get_redis_cache() -> AsyncGenerator[RedisCache, None]:
    """
    Dependency for Redis cache.
    Yields a RedisCache instance that can be used for caching operations.
    """
    async for client in get_redis_client():
        yield RedisCache(client)
