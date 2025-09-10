"""
Session-related custom exceptions.

This module defines specialized exceptions for handling session operations
within the application. These exceptions provide precise error reporting
for common session management scenarios, improving code readability and
enabling consistent error handling in service and API layers.

Exceptions:
    - SessionNotFoundError: Raised when a session is not found.
    - ActiveSessionNotFoundError: Raised when no active session exists for a user.
    - ActiveSessionDeletionError: Raised when deletion of an active session is attempted.
    - DuplicateSessionTitleError: Raised when a session title already exists for the user.
"""


class SessionNotFoundError(Exception):
    """
    Raised when a session is not found in the database.

    This exception is typically used in service or repository layers when
    a query for a specific session by ID or other criteria returns no results.
    """

    ...


class ActiveSessionNotFoundError(Exception):
    """
    Raised when no active session exists for a user.

    This exception is used when operations require an active session
    but none exists, e.g., resuming or updating a current session.
    """

    ...


class ActiveSessionDeletionError(Exception):
    """
    Raised when attempting to delete an active session which is not allowed.

    Ensures that business rules preventing deletion of ongoing sessions
    are enforced.
    """

    ...


class DuplicateSessionTitleError(Exception):
    """
    Raised when a session with the same title already exists for the user.

    Helps maintain uniqueness of session titles per user and prevents
    conflicts during creation or update operations.
    """

    ...
