"""
...
"""

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer


from core.db import db_manager
from services.agent import AgentService

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
    stream = AgentService.stream(question=question)

    return StreamingResponse(stream, media_type="text/event-stream")
