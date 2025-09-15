"""
...
"""

from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from core.enums import StorageType
from models.base import Base


class File(Base):
    """
    ...
    """

    user_id: Mapped[int] = mapped_column(nullable=False)
    file_name: Mapped[str] = mapped_column(nullable=False)
    file_description: Mapped[str] = mapped_column(nullable=False)
    storage_type: Mapped[StorageType] = mapped_column(
        SQLEnum(StorageType, name="storage_type", native_enum=True), nullable=False
    )
    storage_uri: Mapped[str] = mapped_column(nullable=False)
    data_summary: Mapped[str] = mapped_column(nullable=False)
