"""
...
"""

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer


from core.db import db_manager
from core.security import get_current_user_id
from services.agent import AgentService
from services.session import session_service
from services.file import file_service

router = APIRouter(prefix="/agent", tags=["Agent"])

# OAuth2 password bearer scheme for extracting token from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


@router.post("/stream")
async def stream(
    question: str,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(db_manager.get_db),
):
    """
    ...
    """

    # Get user ID from token
    user_id = get_current_user_id(token)

    # Get currently active session ID
    session_id = session_service.get_active_session_id(db=db, user_id=user_id)

    # Get currently active file for the session
    active_file = file_service.get_active_file(
        db=db, user_id=user_id, session_id=session_id
    )

    stream = AgentService.stream(question=question, storage_uri=active_file.storage_uri)

    return StreamingResponse(stream, media_type="text/event-stream")
