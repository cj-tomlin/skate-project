from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import DATABASE_URL, REDIS_URL
import redis.asyncio as redis

# Define the base for SQLAlchemy models
Base = declarative_base()

# Create an asynchronous engine for PostgreSQL
engine = create_async_engine(DATABASE_URL, echo=True)

# Configure sessionmaker for async sessions
async_session = sessionmaker(  # type: ignore
    bind=engine, class_=AsyncSession, autocommit=False, autoflush=False
)


# Dependency for database session
async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()  # Ensure session is closed after use


# Create Redis client
redis_client = redis.from_url(REDIS_URL, decode_responses=True)


# Dependency to interact with Redis
async def get_redis():
    try:
        return redis_client
    except Exception as e:
        # Handle Redis connection error
        raise ConnectionError(f"Could not connect to Redis: {e}")
