from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from fastapi import Depends


async def get_db_session(db: AsyncSession = Depends(get_db)):
    """Database session dependency."""
    try:
        yield db
    finally:
        await db.close()  # Ensure the session is properly closed
