"""
User model definition.

This module defines the `User` SQLAlchemy ORM model, which represents
registered users within the application. It extends the shared `Base`
class to include auditing fields (`id`, `created_at`) and introduces
user-specific fields such as `email` and `password`.
"""

from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class User(Base):
    """
    ORM model representing an application user.

    Inherits from `Base`, providing an auto-incrementing primary key (`id`)
    and creation timestamp (`created_at`). Adds fields for user credentials.

    Attributes:
        email: Unique email address of the user.
        password: Securely hashed password of the user.
    """

    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
