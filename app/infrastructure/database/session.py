from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Create an asynchronous engine for PostgreSQL
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
)

# Configure sessionmaker for async sessions
async_session_factory = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncSession:
    """
    Dependency for database session.
    Yields a SQLAlchemy AsyncSession that will be automatically closed.
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()  # Ensure session is closed after use
