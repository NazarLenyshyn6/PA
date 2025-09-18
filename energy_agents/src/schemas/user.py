"""
Pydantic schemas for user data.

Defines request and response models for creating users,
reading user info, and internal representation including passwords.
"""

from typing import Optional
from datetime import datetime

from pydantic import EmailStr, Field

from schemas.base import BaseSchema


class UserCreate(BaseSchema):
    """Schema for creating a new user.

    Attributes:
        email (EmailStr): User email address.
        password (str): User password (minimum 8 characters).
    """

    email: EmailStr
    password: str = Field(min_length=8)


class UserRead(BaseSchema):
    """Schema for returning user information in responses.

    Attributes:
        id (int): Unique user ID.
        email (EmailStr): User email address.
        created_at (datetime): Timestamp of user creation.
    """

    id: int
    email: EmailStr
    created_at: datetime


class UserInDB(BaseSchema):
    """Schema for internal user representation including password.

    Attributes:
        id (Optional[int]): Unique user ID (may be None before creation).
        password (str): Hashed user password.
    """

    id: Optional[int] = None
    password: str
