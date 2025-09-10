"""
Session ORM model.

This module defines the `Session` database model, representing user sessions
in the application. Each session has a unique UUID, is associated with a user,
and tracks its active state and title.

Attributes:
    - id (UUID): Primary key, auto-generated using PostgreSQL `gen_random_uuid()`.
    - user_id (int): Foreign key reference to the user who owns the session.
    - title (str): Title or name of the session.
    - active (bool): Flag indicating if the session is currently active.
"""

from uuid import UUID
from sqlalchemy import Boolean, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from models.base import Base


class Session(Base):
    """
    Database model for user sessions.

    Inherits from the application's declarative `Base`, providing
    `created_at` and `updated_at` timestamps automatically.
    """

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[int] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, server_default="false")
