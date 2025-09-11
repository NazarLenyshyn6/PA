"""
...
"""

from dataclasses import dataclass
from typing import List


from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from cache.session import SessionCacheManager, session_cache
from core.exceptions.session import (
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
    ...
    """

    session_cache: SessionCacheManager

    def create_session(self, db: Session, session_data: SessionCreate) -> SessionRead:
        """
        ...
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
        ...
        """
        db_sessions = SessionRepository.get_sessions(db=db, user_id=user_id)
        return [SessionRead.model_validate(session) for session in db_sessions]

    def get_active_session_id(self, db: Session, user_id: int) -> str:
        """
        ...
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
        ...
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
        ...
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
