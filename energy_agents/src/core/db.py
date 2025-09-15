"""
...
"""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from core.config import settings


class DBManager:
    """
    ...
    """

    def __init__(self, url: str, echo: bool = False):
        """
        ...
        """
        self.engine = create_engine(url=url, echo=echo)
        self.session_factory = sessionmaker(
            bind=self.engine, autocommit=False, autoflush=False
        )

    def get_db(self) -> Generator[Session, None, None]:
        """
        ...
        """
        db = self.session_factory()
        try:
            yield db
        finally:
            db.close()


# Global DBManager instance configured with application settings
db_manager = DBManager(url=settings.postgres.URL)
