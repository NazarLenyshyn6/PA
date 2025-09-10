"""
File schemas for request and response models.

This module defines Pydantic schemas for file-related operations,
including creating, reading, and representing the currently active
file for a user. These schemas enforce type validation and
data consistency across API endpoints.
"""

from core.enums import StorageType
from schemas.base import BaseSchema


class FileCreate(BaseSchema):
    """
    Schema for creating a new file record.

    Attributes:
        file_name: Name of the file being uploaded.
        storage_uri: URI of the file in the storage backend
                     (e.g., "local://...", "s3://...").
        storage_type: Type of storage backend (from `StorageType` enum).
        user_id: ID of the user who owns the file.
    """

    file_name: str
    storage_uri: str
    storage_type: StorageType
    user_id: int


class FileRead(BaseSchema):
    """
    Schema for reading file metadata.

    Excludes user_id and storage_type for privacy and simplicity
    when returning file information to clients.

    Attributes:
        file_name: Name of the file.
        storage_uri: URI of the file in the storage backend.
    """

    file_name: str
    storage_uri: str


class ActiveFile(BaseSchema):
    """
    Schema representing the currently active file for a user.

    Attributes:
        file_name: Name of the active file.
    """

    file_name: str
