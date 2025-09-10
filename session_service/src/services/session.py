"""
Session service module.

This module defines the `SessionService` class responsible for handling
business logic related to user sessions. It integrates with the
SessionRepository for database operations and SessionCacheManager for caching
active session IDs. This service enforces rules such as unique session titles,
single active session per user, and proper caching of active sessions.

Components:
    - SessionService: Provides methods for creating, retrieving, activating,
      and deleting user sessions.
    - session_service: Singleton instance of SessionService with Redis cache.
"""

from dataclasses import dataclass
from typing import List


from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from cache.session import SessionCacheManager, session_cache
from core.exceptions import (
    ActiveSessionNotFoundError,
    SessionNotFoundError,
    ActiveSessionDeletionError,
    DuplicateSessionTitleError,
)
from schemas.session import SessionRead, SessionCreate
from repositories.session import SessionRepository


@dataclass
class SessionService:
    """
    Service class for user session business logic.

    Attributes:
        session_cache (SessionCacheManager): Cache manager for active session IDs.
    """

    session_cache: SessionCacheManager

    def create_session(self, db: Session, session_data: SessionCreate) -> SessionRead:
        """
        Create a new session for a user and activate it.

        Steps:
            1. Create session in DB (enforcing unique title).
            2. Deactivate current active session in DB and cache.
            3. Set the new session as active.
            4. Cache the new active session ID.

        Args:
            db (Session): SQLAlchemy session object.
            session_data (SessionCreate): Data for creating a session.

        Raises:
            HTTPException: If session title already exists (409 CONFLICT).

        Returns:
            SessionRead: Newly created and activated session.
        """

        # Create new session
        try:
            db_session = SessionRepository.create_session(
                db=db, session_data=session_data
            )
        except DuplicateSessionTitleError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Session with title '{session_data.title}' already exists for the user_id={session_data.user_id}",
            )

        # Deactivate current active session if any (DB + Cache)
        try:
            SessionRepository.deactivate_active_session(
                db=db, user_id=session_data.user_id
            )
            self.session_cache.deactivate_active_session_id(
                user_id=str(session_data.user_id)
            )
        except ActiveSessionNotFoundError:
            ...

        # Activate new session
        SessionRepository.set_active_session(
            db=db, user_id=db_session.user_id, title=db_session.title
        )

        # Cache active session id
        self.session_cache.cache_active_session_id(
            user_id=str(db_session.user_id), session_id=str(db_session.id)
        )

        session = SessionRead.model_validate(db_session)
        return session

    def get_sessions(self, db: Session, user_id: int) -> List[SessionRead]:
        """
        Retrieve all sessions for a given user.

        Args:
            db: SQLAlchemy session object.
            user_id: ID of the user.

        Returns:
            List[SessionRead]: List of session objects for the user.
        """
        db_sessions = SessionRepository.get_sessions(db=db, user_id=user_id)
        return [SessionRead.model_validate(session) for session in db_sessions]

    def get_active_session_id(self, db: Session, user_id: int) -> str:
        """
        Get the currently active session ID for a user.

        Uses cache first, falls back to the database if not found.

        Args:
            db: SQLAlchemy session object.
            user_id: ID of the user.

        Raises:
            HTTPException: If no active session exists (404 NOT FOUND).

        Returns:
            str: Active session ID.
        """
        cached_active_session_id = self.session_cache.get_active_session_id(
            user_id=str(user_id)
        )
        if cached_active_session_id:
            return cached_active_session_id

        # Fallback to DB
        db_session = SessionRepository.get_active_session(db=db, user_id=user_id)
        if db_session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No active session found for user_id={user_id}",
            )
        session_id = str(db_session.id)

        # Cache for future
        self.session_cache.cache_active_session_id(
            user_id=str(user_id), session_id=session_id
        )
        return session_id

    def set_active_session(self, db: Session, user_id: int, title: str) -> dict:
        """
        Set a session as active for a user.

        Deactivates the current active session (if any) and activates the new one.
        Updates the cache accordingly.

        Args:
            db: SQLAlchemy session object.
            user_id: ID of the user.
            title: Title of the session to activate.

        Raises:
            HTTPException: If session is not found (404 NOT FOUND).

        Returns:
            dict: Confirmation message with session title and user_id.
        """

        # Get session to activate
        db_session = SessionRepository.get_session_by_title(
            db=db, user_id=user_id, title=title
        )
        if db_session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with title '{title}' not found for user_id={user_id}",
            )

        # Get current active session, if exists, deactivate it
        db_active_session = SessionRepository.get_active_session(db=db, user_id=user_id)
        if db_active_session:
            SessionRepository.deactivate_active_session(db=db, user_id=user_id)
            self.session_cache.deactivate_active_session_id(user_id=str(user_id))

        # Set new active session
        SessionRepository.set_active_session(db=db, user_id=user_id, title=title)

        # Cache new active session id
        self.session_cache.cache_active_session_id(
            user_id=str(user_id), session_id=str(db_session.id)
        )

        return {"detail": f"'{title}' set as active session for user_id={user_id}"}

    def delete_session(self, db: Session, user_id: int, title: str) -> dict:
        """
        Delete a session by title for a user.

        Args:
            db: SQLAlchemy session object.
            user_id: ID of the user.
            title: Title of the session to delete.

        Raises:
            HTTPException: If session not found (404) or active session deletion attempted (400).

        Returns:
            dict: Confirmation message.
        """
        try:
            SessionRepository.delete_session(db=db, user_id=user_id, title=title)
            return {"detail": "Session deleted successfully"}
        except SessionNotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Session not found"
            )

        except ActiveSessionDeletionError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete an active session; please deactivate it first",
            )


# Singleton instance of SessionService
session_service = SessionService(session_cache=session_cache)
