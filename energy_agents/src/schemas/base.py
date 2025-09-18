"""
Base Pydantic schema for all models.

Provides a common configuration for attribute-based initialization
and support for arbitrary types.
"""

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema class with default Pydantic configuration.

    Attributes:
        model_config (ConfigDict): Configuration enabling:
            - `from_attributes=True`: Initialize model from object attributes.
            - `arbitrary_types_allowed=True`: Allow non-Pydantic types.
    """

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
