"""
Database management module.

This module provides a centralized database manager for handling SQLAlchemy
engine and session lifecycle management. It encapsulates the logic for
creating connections to the PostgreSQL database and ensures proper session
closing using context-style generators.

It uses application settings (`core.config.settings`) to configure
the database connection.
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from core.config import settings


class DBManager:
    """
    Database manager for handling SQLAlchemy engine and session factories.

    This class abstracts database connection and session management,
    providing a consistent and safe way to interact with the database
    throughout the application.

    Attributes:
        engine: SQLAlchemy engine bound to the configured database.
        session_factory: Factory that creates SQLAlchemy `Session` objects.
    """

    def __init__(self, url: str, echo: bool = False):
        """
        Initialize the database manager.

        Args:
            url (str): Database connection URL.
            echo (bool, optional): Whether SQLAlchemy should log all SQL statements
                to stdout. Defaults to False.
        """
        self.engine = create_engine(url=url, echo=echo)
        self.session_factory = sessionmaker(
            bind=self.engine, autocommit=False, autoflush=False
        )

    def get_db(self) -> Generator[Session, None, None]:
        """
        Provide a database session for use within application logic.

        This method is designed to be used with dependency injection
        (e.g., in FastAPI routes). It ensures that the session is
        properly closed after use, even in case of exceptions.

        Yields:
            Session: A SQLAlchemy session object bound to the configured database.
        """
        db = self.session_factory()
        try:
            yield db
        finally:
            db.close()


# Global DBManager instance configured with application settings
db_manager = DBManager(url=settings.postgres.URL)
