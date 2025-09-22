"""
Database manager for SQLAlchemy sessions.

Provides a session factory and context-managed session generator
for use throughout the application.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from core.config import settings


class DBManager:
    """Manager for SQLAlchemy database connections and sessions."""

    def __init__(self, url: str, echo: bool = False):
        """Initialize the database engine and session factory.

        Args:
            url (str): Database connection URL.
            echo (bool, optional): Enable SQL query logging. Defaults to False.
        """
        self.engine = create_engine(url=url, echo=echo)
        self.session_factory = sessionmaker(
            bind=self.engine, autocommit=False, autoflush=False
        )

    def get_db(self) -> Generator[Session, None, None]:
        """Provide a transactional SQLAlchemy session as a generator.

        Yields:
            Session: SQLAlchemy session instance.

        Ensures the session is closed after use.
        """
        db = self.session_factory()
        try:
            yield db
        finally:
            db.close()


# Global DBManager instance configured with application settings
db_manager = DBManager(url=settings.postgres.URL)
