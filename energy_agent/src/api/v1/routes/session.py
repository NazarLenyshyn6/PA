"""
...
"""

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer

from core.db import db_manager
from core.security import get_current_user_id
from schemas.session import SessionCreate, NewSession
from services.session import session_service


router = APIRouter(prefix="/sessions", tags=["Sessions"])

# OAuth2 password bearer scheme for extracting token from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


@router.get("/")
def get_sessions(
    db: Session = Depends(db_manager.get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    ...
    """
    user_id = get_current_user_id(token)
    return session_service.get_sessions(db=db, user_id=user_id)


@router.get("/active")
def get_active_session_id(
    db: Session = Depends(db_manager.get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    ...
    """
    user_id = get_current_user_id(token)
    return session_service.get_active_session_id(db=db, user_id=user_id)


@router.post("/")
def create_session(
    new_session: NewSession,
    db: Session = Depends(db_manager.get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    ...
    """
    user_id = get_current_user_id(token)
    session_data = SessionCreate(user_id=user_id, title=new_session.title)
    return session_service.create_session(db=db, session_data=session_data)


@router.post("/active/{title}")
def set_active_session(
    title: str,
    db: Session = Depends(db_manager.get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    ...
    """
    user_id = get_current_user_id(token)
    return session_service.set_active_session(db=db, user_id=user_id, title=title)


@router.delete("/{title}")
def delete_session(
    title: str,
    db: Session = Depends(db_manager.get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    ...
    """
    user_id = get_current_user_id(token)
    return session_service.delete_session(db=db, user_id=user_id, title=title)
