"""
Base SQLAlchemy declarative model.

Provides common fields and configuration for all models,
including auto-incrementing primary key and creation timestamp.
"""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column


class Base(DeclarativeBase):
    """Abstract base class for all SQLAlchemy models.

    Attributes:
        id (int): Auto-incrementing primary key.
        created_at (datetime): Timestamp of record creation (UTC).
    """

    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Generate table name automatically from class name.

        Converts the class name to lowercase and appends 's'.

        Returns:
            str: Table name for the model.
        """
        return f"{cls.__name__.lower()}s"
