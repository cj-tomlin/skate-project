"""
Database helpers for tests.
"""

import contextlib
from typing import Generator, Any, Dict, Optional, List, Type

from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import DeclarativeMeta

from app.infrastructure.database.base import Base


def reset_table_sequence(db: Session, table_name: str) -> None:
    """
    Reset the sequence for a table's primary key.
    Useful after truncating tables in PostgreSQL.

    Args:
        db: SQLAlchemy session
        table_name: Name of the table to reset sequence for
    """
    db.execute(
        text(f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), 1, false)")
    )


@contextlib.contextmanager
def temp_db_records(
    db: Session, model_class: Type[DeclarativeMeta], records_data: List[Dict[str, Any]]
) -> Generator[List[Any], None, None]:
    """
    Context manager for creating temporary database records for tests.
    Records are automatically deleted when the context exits.

    Args:
        db: SQLAlchemy session
        model_class: The SQLAlchemy model class
        records_data: List of dictionaries with record data

    Yields:
        List of created model instances

    Usage:
        with temp_db_records(db, User, [{"username": "temp1"}, {"username": "temp2"}]) as users:
            # Test code using the temporary users
            assert len(users) == 2
            # Records are automatically deleted after the context exits
    """
    records = []
    try:
        # Create records
        for data in records_data:
            record = model_class(**data)
            db.add(record)
            records.append(record)
        db.commit()

        # Refresh records to get generated values
        for record in records:
            db.refresh(record)

        yield records
    finally:
        # Clean up records
        for record in records:
            db.delete(record)
        db.commit()


def truncate_tables(db: Session, *table_names: str) -> None:
    """
    Truncate specified tables and reset their sequences.

    Args:
        db: SQLAlchemy session
        table_names: Names of tables to truncate
    """
    for table_name in table_names:
        db.execute(text(f"TRUNCATE TABLE {table_name} CASCADE"))
        reset_table_sequence(db, table_name)
    db.commit()


def truncate_all_tables(db: Session) -> None:
    """
    Truncate all tables in the database and reset their sequences.

    Args:
        db: SQLAlchemy session
    """
    # Get all table names from metadata
    table_names = [table.name for table in Base.metadata.sorted_tables]
    truncate_tables(db, *table_names)


def count_records(db: Session, model_class: Type[DeclarativeMeta]) -> int:
    """
    Count the number of records for a model.

    Args:
        db: SQLAlchemy session
        model_class: The SQLAlchemy model class

    Returns:
        Number of records
    """
    return db.query(model_class).count()


def find_by_field(
    db: Session, model_class: Type[DeclarativeMeta], field_name: str, field_value: Any
) -> Optional[Any]:
    """
    Find a record by a specific field value.

    Args:
        db: SQLAlchemy session
        model_class: The SQLAlchemy model class
        field_name: Name of the field to search by
        field_value: Value to search for

    Returns:
        Found record or None
    """
    return (
        db.query(model_class)
        .filter(getattr(model_class, field_name) == field_value)
        .first()
    )
