"""
Base SQLAlchemy declarative model.

This module defines a base class for all SQLAlchemy ORM models in the application.
It provides automatic timestamp columns (`created_at` and `updated_at`) and
a default table naming convention based on class names.

Components:
    - Base: Abstract declarative base class for SQLAlchemy models.
"""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Abstract base class for all database models.

    Provides:
        - Automatic `created_at` and `updated_at` timestamp columns.
        - Default table name derived from class name in lowercase plural form.

    Attributes:
        created_at: Timestamp of row creation (auto-generated).
        updated_at: Timestamp of last row update (auto-updated).
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

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Generate the table name automatically based on the class name.

        Returns:
            str: Table name in pluralized lowercase format.
                 Example: `User` → `users`, `Order` → `orders`.
        """
        return f"{cls.__name__.lower()}s"
