"""
Enumeration for supported storage backends.

Defines the types of storage that can be used for file management.
"""

from enum import Enum


class StorageType(str, Enum):
    """Supported storage types."""

    LOCAL = "local"
