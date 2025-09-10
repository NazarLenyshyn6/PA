"""
User schemas.

This module defines Pydantic schemas for user-related operations. These schemas
are responsible for validating and structuring user data at different stages
of the application's workflow, including creation, reading from the database,
and internal persistence.

Schemas:
    - UserCreate: Schema for validating incoming user registration data.
    - UserRead: Schema for serializing user data returned in API responses.
    - UserInDB: Schema for representing internal database user objects.
"""

from typing import Optional
from datetime import datetime

from pydantic import EmailStr, Field

from schemas.base import BaseSchema


class UserCreate(BaseSchema):
    """
    Schema for creating a new user.

    Attributes:
        email: The user's unique email address. Validated to ensure
            proper email format.
        password: The user's password. Must be at least 8 characters long.
    """

    email: EmailStr
    password: str = Field(min_length=8)


class UserRead(BaseSchema):
    """
    Schema for reading user data (e.g., in API responses).

    Attributes:
        id: Unique identifier of the user in the database.
        email: The user's registered email address.
        created_at: Timestamp indicating when the user was created.
    """

    id: int
    email: EmailStr
    created_at: datetime


class UserInDB(BaseSchema):
    """
    Schema representing a user stored in the database.

    This schema is typically used internally and should not be exposed
    directly in API responses, since it contains sensitive fields.

    Attributes:
        id: Database identifier of the user. May be None
            before persistence.
        password: The hashed password stored in the database.
    """

    id: Optional[int] = None
    password: str
