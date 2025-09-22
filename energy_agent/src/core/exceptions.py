"""
Custom exceptions for file handling.

Defines errors for duplicate filenames and unsupported file extensions.
"""


class DuplicateFileNameError(Exception):
    """Raised when a file with the same name already exists for a user."""

    ...


class UnsupportedFileExtensionError(Exception):
    """Raised when a file has an unsupported or invalid extension."""

    ...
