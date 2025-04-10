from typing import AsyncGenerator, Optional, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.session import async_session_factory

T = TypeVar("T")


class UnitOfWork:
    """
    Unit of Work pattern implementation for managing database transactions.
    Ensures that multiple database operations are executed atomically.
    """

    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session
        self._external_session = session is not None

    async def __aenter__(self) -> "UnitOfWork":
        if self._session is None:
            self._session = async_session_factory()
            await self._session.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if not self._external_session and self._session is not None:
            if exc_type is not None:
                await self._session.rollback()
            else:
                await self._session.commit()
            await self._session.__aexit__(exc_type, exc_val, exc_tb)
            self._session = None

    @property
    def session(self) -> AsyncSession:
        """Get the current session."""
        if self._session is None:
            raise ValueError("UnitOfWork not initialized or already closed")
        return self._session

    async def commit(self):
        """Commit the current transaction."""
        if self._session is None:
            raise ValueError("UnitOfWork not initialized or already closed")
        await self._session.commit()

    async def rollback(self):
        """Rollback the current transaction."""
        if self._session is None:
            raise ValueError("UnitOfWork not initialized or already closed")
        await self._session.rollback()


async def get_unit_of_work(
    session: Optional[AsyncSession] = None,
) -> AsyncGenerator[UnitOfWork, None]:
    """
    Dependency for unit of work.
    Can optionally use an existing session.
    """
    async with UnitOfWork(session) as uow:
        yield uow
