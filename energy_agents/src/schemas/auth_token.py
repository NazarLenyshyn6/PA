"""
...
"""

from typing import Optional

from schemas.base import BaseSchema


class Token(BaseSchema):
    """
    ....
    """

    access_token: str
    token_type: str


class TokenData(BaseSchema):
    """
    ...
    """

    user_id: Optional[str] = None
