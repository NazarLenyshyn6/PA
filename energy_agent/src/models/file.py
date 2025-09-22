"""
SQLAlchemy model for user file records.

Stores metadata, storage location, and summary information
for each file uploaded by a user.
"""

from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from core.enums import StorageType
from models.base import Base


class File(Base):
    """Model representing a user-uploaded file.

    Attributes:
        user_id (int): ID of the user who owns the file.
        file_name (str): Name of the file.
        file_description (str): Description of the file content.
        storage_type (StorageType): Backend storage type (e.g., local).
        storage_uri (str): URI or path where the file is stored.
        data_summary (str): Summary of the file's content.
    """

    user_id: Mapped[int] = mapped_column(nullable=False)
    file_name: Mapped[str] = mapped_column(nullable=False)
    file_description: Mapped[str] = mapped_column(nullable=False)
    storage_type: Mapped[StorageType] = mapped_column(
        SQLEnum(StorageType, name="storage_type", native_enum=True), nullable=False
    )
    storage_uri: Mapped[str] = mapped_column(nullable=False)
    data_summary: Mapped[str] = mapped_column(nullable=False)
