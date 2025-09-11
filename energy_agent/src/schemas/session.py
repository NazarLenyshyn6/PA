"""
...
"""

from uuid import UUID

from schemas.base import BaseSchema


class SessionCreate(BaseSchema):
    """
    ...
    """

    user_id: int
    title: str
    active: bool = False


class SessionRead(BaseSchema):
    """
    ...
    """

    id: UUID
    user_id: int
    title: str
    active: bool


class NewSession(BaseSchema):
    """
    ...
    """

    title: str
