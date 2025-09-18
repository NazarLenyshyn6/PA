"""
Pydantic schemas for file data.

Defines request and response models for creating files,
returning file metadata, and optional in-memory data representation.
"""

from typing import Any, Optional


from core.enums import StorageType
from schemas.base import BaseSchema


class FileCreate(BaseSchema):
    """Schema for creating a file record in the database.

    Attributes:
        user_id (int): ID of the user who owns the file.
        file_name (str): Name of the file.
        file_description (str): Description of the file content.
        storage_type (StorageType): Type of storage backend used.
        storage_uri (str): URI or path where the file is stored.
        data_summary (str): Summary of the file contents.
    """

    user_id: int
    file_name: str
    file_description: str
    storage_type: StorageType
    storage_uri: str
    data_summary: str


class FileData(BaseSchema):
    """Schema representing file metadata and optional in-memory data.

    Attributes:
        file_name (str): Name of the file.
        file_description (str): Description of the file content.
        data_summary (str): Summary of the file contents.
        storage_uri (str): URI or path where the file is stored.
        df (Optional[Any]): Optional in-memory representation of the file
            (e.g., a Pandas DataFrame).
    """

    file_name: str
    file_description: str
    data_summary: str
    storage_uri: str
    df: Optional[Any] = None

    def format(self) -> str:
        """Return a human-readable string representation of file metadata.

        Returns:
            str: Formatted file information.
        """
        return (
            f"File Name: {self.file_name}\n"
            f"File Description: {self.file_description}\n"
            f"Data Summary: {self.data_summary}\n"
        )
