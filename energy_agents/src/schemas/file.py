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
