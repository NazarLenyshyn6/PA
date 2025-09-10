"""
Database base model module.

This module defines the declarative SQLAlchemy `Base` class used as the
foundation for all ORM models in the application. It introduces common
timestamp fields for entity lifecycle tracking (`created_at` and
`updated_at`), ensuring consistency across all derived database models.

Classes:
    Base: An abstract declarative base class providing common
          timestamp columns for model inheritance.
"""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Abstract declarative base class for all ORM models.

    This class serves as the base for all SQLAlchemy ORM models within the
    application. It provides automatic timestamp fields that are
    initialized and updated by the database server:

    Attributes:
        created_at: Timestamp when the record is first created.
            Automatically set by the database to the current time.
        updated_at: Timestamp when the record is last updated.
            Automatically set by the database to the current time on insert
            and updated on every modification.
    """

    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
