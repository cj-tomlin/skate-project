from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import DATABASE_URL, REDIS_URL
import redis.asyncio as redis

# Create an asynchronous engine for PostgreSQL
engine = create_async_engine(DATABASE_URL, echo=True)

# Configure session maker for async mode
async_session = sessionmaker(  # type: ignore
    bind=engine, class_=AsyncSession, autocommit=False, autoflush=False
)


# Dependency for database session
async def get_db():
    async with async_session() as session:
        yield session


# Create Redis connection
redis_client = redis.from_url(REDIS_URL, decode_responses=True)


# Dependency to interact with Redis
async def get_redis():
    return redis_client
