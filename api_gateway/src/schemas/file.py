"""
This module defines request models related to active file operations.

Models:
    ActiveFileRequest: Schema for validating requests that specify
    the currently active file by name.
"""

from pydantic import BaseModel


class ActiveFileRequest(BaseModel):
    """
    Data model representing a request to set or reference an active file.

    Attributes:
        file_name: The name of the active file being referenced or set.
    """

    file_name: str
