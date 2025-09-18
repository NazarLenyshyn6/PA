"""
Pydantic schemas for authentication tokens.

Defines models for access token responses and decoded token data.
"""

from typing import Optional

from schemas.base import BaseSchema


class Token(BaseSchema):
    """Schema for returning an access token.

    Attributes:
        access_token (str): JWT access token string.
        token_type (str): Type of the token, e.g., "bearer".
    """

    access_token: str
    token_type: str


class TokenData(BaseSchema):
    """Schema representing decoded token data.

    Attributes:
        user_id (Optional[str]): User ID extracted from the token,
            if available.
    """

    user_id: Optional[str] = None
