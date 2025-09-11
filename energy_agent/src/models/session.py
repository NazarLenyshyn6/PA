"""
...
"""

from uuid import UUID
from sqlalchemy import Boolean, text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from models.base import Base


class Session(Base):
    """
    ...
    """

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[int] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, server_default="false")
