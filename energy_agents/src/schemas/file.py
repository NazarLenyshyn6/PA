"""
...
"""

from typing import Any, Optional


from core.enums import StorageType
from schemas.base import BaseSchema


class FileCreate(BaseSchema):
    """
    ...
    """

    user_id: int
    file_name: str
    file_description: str
    storage_type: StorageType
    storage_uri: str
    data_summary: str


class FileData(BaseSchema):
    """
    ...
    """

    file_name: str
    file_description: str
    data_summary: str
    storage_uri: str
    df: Optional[Any] = None

    def format(self) -> str:
        return (
            f"File Name: {self.file_name}\n"
            f"File Description: {self.file_description}\n"
            f"Data Summary: {self.data_summary}\n"
        )
