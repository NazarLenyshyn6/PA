"""
Session schemas module.

This module defines Pydantic schemas for session-related data validation and
serialization. These schemas are used in API requests and responses to enforce
type safety and ensure consistent data structure for session operations.

Schemas:
    - SessionCreate: Schema for creating a new session.
    - SessionRead: Schema for reading session data from the database.
    - NewSession: Minimal schema for creating a session with only a title.
"""

from uuid import UUID

from schemas.base import BaseSchema


class SessionCreate(BaseSchema):
    """
    Schema for creating a new user session.

    Attributes:
        user_id: ID of the user who owns the session.
        title: Title or name of the session.
        active: Flag indicating if the session is active. Defaults to False.
    """

    user_id: int
    title: str
    active: bool = False


class SessionRead(BaseSchema):
    """
    Schema for reading session data from the database.

    Attributes:
        id: Unique session identifier.
        user_id: ID of the user who owns the session.
        title : Title of the session.
        active: Indicates if the session is currently active.
    """

    id: UUID
    user_id: int
    title: str
    active: bool


class NewSession(BaseSchema):
    """
    Minimal schema for creating a new session with only a title.

    Attributes:
        title: Title or name of the session.
    """

    title: str
