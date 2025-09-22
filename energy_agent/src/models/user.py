"""
SQLAlchemy model for application users.

Stores user credentials and inherits common fields like `id` and `created_at`
from the Base model.
"""

from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class User(Base):
    """Model representing an application user.

    Attributes:
        email (str): Unique email address of the user.
        password (str): Hashed password of the user.
    """

    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
