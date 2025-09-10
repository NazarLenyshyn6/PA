"""
File model.

This module defines the `File` SQLAlchemy model representing files uploaded
by users and stored in different storage backends (local, cloud, etc.).

Attributes include metadata such as name, description, storage URI, summary,
storage type, and associated user.
"""

from sqlalchemy import Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from core.enums import StorageType
from models.base import Base


class File(Base):
    """
    SQLAlchemy model for a user-uploaded file.

    Attributes:
        file_name: Name of the uploaded file.
        storage_uri: URI of the file in the storage backend
                     (e.g., "local://...", "s3://...").
        storage_type: Storage backend type (from `StorageType` enum).
        user_id: ID of the user who uploaded the file.
    """

    file_name: Mapped[str] = mapped_column(nullable=False)
    storage_uri: Mapped[str] = mapped_column(nullable=False)
    storage_type: Mapped[StorageType] = mapped_column(
        SQLEnum(StorageType, name="storage_type", native_enum=True), nullable=False
    )
    user_id: Mapped[int] = mapped_column(nullable=False)
