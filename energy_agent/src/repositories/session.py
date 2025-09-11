"""
...
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from core.exceptions.session import (
    SessionNotFoundError,
    ActiveSessionDeletionError,
    DuplicateSessionTitleError,
)
from schemas.session import SessionCreate
from models import session as user_session


class SessionRepository:
    """
    ...
    """

    @classmethod
    def create_session(
        cls, db: Session, session_data: SessionCreate
    ) -> user_session.Session:
        """
        ...
        """
        db_existing_session = cls.get_session_by_title(
            db=db, user_id=session_data.user_id, title=session_data.title
        )
        if db_existing_session:
            raise DuplicateSessionTitleError("Session with this title already exists.")
        db_session = user_session.Session(**session_data.model_dump())
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session

    @staticmethod
    def get_sessions(db: Session, user_id: int) -> List[user_session.Session]:
        """
        ...
        """
        sessions = (
            db.query(user_session.Session)
            .filter(user_session.Session.user_id == user_id)
            .all()
        )
        return sessions

    @staticmethod
    def get_session_by_title(
        db: Session, user_id: int, title: str
    ) -> Optional[user_session.Session]:
        """
        ...
        """
        session = (
            db.query(user_session.Session)
            .where(
                user_session.Session.user_id == user_id,
                user_session.Session.title == title,
            )
            .first()
        )
        return session

    @staticmethod
    def get_active_session(db: Session, user_id: int) -> user_session.Session:
        """
        ...
        """
        db_session = (
            db.query(user_session.Session)
            .where(
                user_session.Session.user_id == user_id,
                user_session.Session.active,
            )
            .first()
        )
        return db_session

    @staticmethod
    def deactivate_active_session(db: Session, user_id: int) -> None:
        """
        ...
        """
        db_active_session = (
            db.query(user_session.Session)
            .filter(
                user_session.Session.user_id == user_id,
                user_session.Session.active.is_(True),
            )
            .first()
        )
        if db_active_session is None:
            return

        db_active_session.active = False
        db.commit()

    @classmethod
    def set_active_session(cls, db: Session, user_id: int, title: str) -> None:
        """
        ...
        """
        db_session = cls.get_session_by_title(db=db, user_id=user_id, title=title)

        if db_session is None:
            raise SessionNotFoundError(
                f"No session found with title '{title}' for user_id={user_id}"
            )

        cls.deactivate_active_session(db=db, user_id=user_id)
        db_session.active = True
        db.commit()

    @classmethod
    def delete_session(cls, db: Session, user_id: int, title: str) -> None:
        """
        ...
        """
        db_session = cls.get_session_by_title(db=db, user_id=user_id, title=title)
        if db_session is None:
            raise SessionNotFoundError(
                f"No session found with title '{title}' for user_id={user_id}"
            )
        if db_session.active:
            raise ActiveSessionDeletionError(
                f"Cannot delete active session titled '{title}' for user_id={user_id}"
            )
        db.delete(db_session)
        db.commit()
