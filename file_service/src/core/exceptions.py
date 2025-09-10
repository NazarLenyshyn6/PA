"""
Custom file-related exceptions.

This module defines application-specific exceptions for handling
errors related to file operations, such as duplicate filenames
or unsupported file types.
"""


class DuplicateFileNameError(Exception):
    """
    Raised when an attempt is made to create or upload a file
    with a name that already exists in the system.
    """

    ...


class UnsupportedFileExtensionError(Exception):
    """
    Raised when a file with an unsupported extension is provided
    for an operation, such as upload or processing.
    """

    ...
