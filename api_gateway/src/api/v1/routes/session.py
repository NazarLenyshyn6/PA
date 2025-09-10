"""
Session management API routes.

This module provides endpoints for managing user sessions, including
listing all sessions, creating new sessions, retrieving the active session,
setting an active session, and deleting sessions. It uses `SessionClient`
to interact with the backend service. All endpoints require OAuth2 token
authentication.

Endpoints:
    GET /sessions/: List all sessions for the authenticated user.
    GET /sessions/active: Retrieve the currently active session ID.
    POST /sessions/: Create a new session.
    POST /sessions/active/{title}: Set a specific session as active.
    DELETE /sessions/{title}: Delete a session by title.
"""

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

from schemas.session import NewSessionRequest
from clients.session import SessionClient

# OAuth2 dependency for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/gateway/auth/login")

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.get("/")
def get_session(token: str = Depends(oauth2_scheme)):
    """
    Retrieve all sessions for the authenticated user.

    Args:
        token: OAuth2 bearer token injected via dependency.

    Returns:
        dict: JSON response containing a list of sessions.
    """
    return SessionClient.get_sessions(token=token)


@router.get("/active")
def get_active_session_id(token: str = Depends(oauth2_scheme)):
    """
    Retrieve the ID of the currently active session.

    Args:
        token: OAuth2 bearer token injected via dependency.

    Returns:
        dict: JSON response containing the active session ID.
    """
    return SessionClient.get_active_session_id(token=token)


@router.post("/")
def create_session(new_session: NewSessionRequest, token: str = Depends(oauth2_scheme)):
    """
    Create a new session with the given title.

    Args:
        new_session: Pydantic model containing the session title.
        token: OAuth2 bearer token injected via dependency.

    Returns:
        dict: JSON response confirming session creation.
    """
    return SessionClient.create_session(token=token, title=new_session.title)


@router.post("/active/{title}")
def set_active_session(title: str, token: str = Depends(oauth2_scheme)):
    """
    Set a specific session as active by title.

    Args:
        title: Title of the session to set as active.
        token: OAuth2 bearer token injected via dependency.

    Returns:
        dict: JSON response confirming the session has been set as active.
    """
    return SessionClient.set_active_session(token=token, title=title)


@router.delete("/{title}")
def delete_session(title: str, token: str = Depends(oauth2_scheme)):
    """
    Delete a session by its title.

    Args:
        title: Title of the session to delete.
        token: OAuth2 bearer token injected via dependency.

    Returns:
        dict: JSON response confirming the session has been deleted.
    """
    return SessionClient.delete_session(token=token, title=title)
