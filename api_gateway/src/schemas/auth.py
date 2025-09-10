"""
This module defines request models used for user authentication and account creation.

Models:
    RegisterRequest: Schema for validating user registration requests,
    including email and password constraints.
"""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """
    Data model representing a user registration request.

    Attributes:
        email: The user's email address. Must be a valid email format.
        password: The user's password. Must have at least 8 characters.
    """

    email: EmailStr
    password: str = Field(min_length=8)
