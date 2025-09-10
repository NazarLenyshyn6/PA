"""
Sessions API routes.

This module defines FastAPI endpoints for managing user sessions.
It integrates with the `session_service` to provide session creation,
retrieval, activation, and deletion functionality for authenticated users.

Endpoints:
    - GET /sessions/: Retrieve all sessions for the current user.
    - GET /sessions/active: Retrieve the currently active session ID.
    - POST /sessions/: Create a new session.
    - POST /sessions/active/{title}: Set a session as active.
    - DELETE /sessions/{title}: Delete a session by title.
"""

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends

from core.db import db_manager
from core.security import get_current_user_id
from schemas.session import SessionCreate, NewSession
from services.session import session_service

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.get("/")
def get_sessions(
    db: Session = Depends(db_manager.get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Retrieve all sessions for the current authenticated user.

    Args:
        db: SQLAlchemy database session dependency.
        user_id: ID of the current authenticated user.

    Returns:
        List[Session]: A list of session objects associated with the user.
    """
    return session_service.get_sessions(db=db, user_id=user_id)


@router.get("/active")
def get_active_session_id(
    db: Session = Depends(db_manager.get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Retrieve the ID of the currently active session for the current user.

    Args:
        db: SQLAlchemy database session dependency.
        user_id: ID of the current authenticated user.

    Returns:
        int | None: ID of the active session, or None if no active session exists.
    """
    return session_service.get_active_session_id(db=db, user_id=user_id)


@router.post("/")
def create_session(
    new_session: NewSession,
    db: Session = Depends(db_manager.get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Create a new session for the current user.

    Args:
        new_session: Incoming data required to create a session (e.g., title).
        db: SQLAlchemy database session dependency.
        user_id: ID of the current authenticated user.

    Returns:
        Session: The newly created session object.
    """
    session_data = SessionCreate(user_id=user_id, title=new_session.title)
    return session_service.create_session(db=db, session_data=session_data)


@router.post("/active/{title}")
def set_active_session(
    title: str,
    db: Session = Depends(db_manager.get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Set a specific session as the active session for the current user.

    Args:
        title: Title of the session to set as active.
        db: SQLAlchemy database session dependency.
        user_id: ID of the current authenticated user.

    Returns:
        Session: The session object that was set as active.
    """
    return session_service.set_active_session(db=db, user_id=user_id, title=title)


@router.delete("/{title}")
def delete_session(
    title: str,
    db: Session = Depends(db_manager.get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Delete a session by its title for the current user.

    Args:
        title: Title of the session to delete.
        db: SQLAlchemy database session dependency.
        user_id: ID of the current authenticated user.

    Returns:
        dict: Confirmation of deletion or relevant status message.
    """
    return session_service.delete_session(db=db, user_id=user_id, title=title)
