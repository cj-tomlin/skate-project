from sqlalchemy.orm import Session
from app.db import get_db
from fastapi import Depends


def get_db_session(db: Session = Depends(get_db)):
    """Database session dependency."""
    try:
        yield db
    finally:
        db.close()  # Ensure the session is properly closed
