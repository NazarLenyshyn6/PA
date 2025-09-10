"""
SQLAlchemy declarative base module.

This module defines the base class for all SQLAlchemy ORM models in the
application. It provides common fields such as an auto-incrementing primary key
(`id`) and a creation timestamp (`created_at`). Additionally, it automatically
generates table names based on the class name.
"""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Abstract base class for all SQLAlchemy ORM models.

    This class provides:
        - An integer primary key (`id`) column.
        - A timestamp column (`created_at`) automatically set at record creation.
        - Automatic table name generation (`__tablename__`) based on the model name.

    Attributes:
        id: Primary key column, auto-incremented by the database.
        created_at: Timestamp of row creation with timezone support.
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
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
