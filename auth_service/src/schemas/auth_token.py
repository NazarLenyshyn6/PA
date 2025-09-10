"""
Authentication token schemas.

This module defines Pydantic schemas for authentication tokens used in the
application. These schemas are responsible for structuring and validating
token-related data exchanged between the API and clients.

Schemas:
    - Token: Represents the access token returned to the client after login.
    - TokenData: Represents the decoded data extracted from a JWT token.
"""

from typing import Optional

from schemas.base import BaseSchema


class Token(BaseSchema):
    """
    Schema representing an authentication token.

    Attributes:
        access_token: The signed JWT access token.
        token_type: The type of the token (commonly "bearer").
    """

    access_token: str
    token_type: str


class TokenData(BaseSchema):
    """
    Schema representing decoded JWT token data.

    This schema is typically used when parsing and validating
    claims extracted from a JWT.

    Attributes:
        user_id: The identifier of the authenticated user.
            Defaults to None if not present.
    """

    user_id: Optional[str] = None
