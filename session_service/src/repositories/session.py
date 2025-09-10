"""
Session repository module.

This module defines the `SessionRepository` class responsible for all
database operations related to user sessions. It handles creation, retrieval,
activation, deactivation, and deletion of session records while enforcing
business rules such as unique titles and active session constraints.

Exceptions:
    - SessionNotFoundError: Raised when a session is not found.
    - ActiveSessionDeletionError: Raised when attempting to delete an active session.
    - DuplicateSessionTitleError: Raised when creating a session with a duplicate title.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from core.exceptions import (
    SessionNotFoundError,
    ActiveSessionDeletionError,
    DuplicateSessionTitleError,
)
from schemas.session import SessionCreate
from models import session as user_session


class SessionRepository:
    """
    Repository class for session-related database operations.

    Provides methods to create, retrieve, update, and delete sessions
    in the database with business rule enforcement.
    """

    @classmethod
    def create_session(
        cls, db: Session, session_data: SessionCreate
    ) -> user_session.Session:
        """
        Create a new session for a user.

        Args:
            db: SQLAlchemy session object.
            session_data: Data for the new session.

        Raises:
            DuplicateSessionTitleError: If a session with the same title exists for the user.

        Returns:
            user_session.Session: The created session object.
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
        Retrieve all sessions for a given user.

        Args:
            db: SQLAlchemy session object.
            user_id: ID of the user.

        Returns:
            List[user_session.Session]: List of user sessions.
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
        Retrieve a session by title for a specific user.

        Args:
            db: SQLAlchemy session object.
            user_id: ID of the user.
            title: Session title to search for.

        Returns:
            Optional[user_session.Session]: Matching session or None if not found.
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
        Retrieve the currently active session for a user.

        Args:
            db: SQLAlchemy session object.
            user_id: ID of the user.

        Returns:
            user_session.Session: Active session object or None if no active session exists.
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
        Deactivate the currently active session for a user.

        Args:
            db: SQLAlchemy session object.
            user_id: ID of the user.
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
        Set a session as active for a user, deactivating any other active session.

        Args:
            db: SQLAlchemy session object.
            user_id: ID of the user.
            title: Title of the session to activate.

        Raises:
            SessionNotFoundError: If the session with the given title does not exist.
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
        Delete a session by title for a user.

        Args:
            db: SQLAlchemy session object.
            user_id: ID of the user.
            title: Title of the session to delete.

        Raises:
            SessionNotFoundError: If no session with the given title exists.
            ActiveSessionDeletionError: If attempting to delete an active session.
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
