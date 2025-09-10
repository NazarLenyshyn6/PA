"""
Storage type enumeration.

This module defines the types of storage supported by the application.
It uses Python's `Enum` to provide a type-safe way to specify storage options.

Classes:
    - StorageType: Enum representing available storage types.
"""

from enum import Enum


class StorageType(str, Enum):
    """
    Enum representing supported storage types.

    Attributes:
        LOCAL: Local filesystem storage.
        # Future storage types can be added here, e.g., S3, GCS, etc.
    """

    LOCAL = "local"
