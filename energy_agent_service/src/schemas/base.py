"""
Base Pydantic schema module.

This module defines a reusable base schema for all Pydantic models
used in the application. It ensures consistent behavior across schemas,
particularly when integrating with SQLAlchemy ORM models.
"""

from pydantic import BaseModel


class BaseSchema(BaseModel):
    """
    Base schema for all Pydantic models.

    This schema enables automatic population of fields from ORM model
    attributes, allowing seamless integration between SQLAlchemy models
    and Pydantic schemas.

    Configuration:
        from_attributes: Enables support for loading schema data
            directly from ORM objects.
    """

    model_config = {"from_attributes": True}
