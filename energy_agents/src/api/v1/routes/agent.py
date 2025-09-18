"""
Agent interaction API routes.

Provides endpoints for streaming AI agent responses based on:
- User question
- Structured data from uploaded files
- Unstructured data from external PDFs
"""

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordBearer


from core.db import db_manager
from core.secutiry import get_current_user_id
from services.agent import AgentService
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
    """Stream AI agent responses to the client as Server-Sent Events (SSE).

    Combines structured data (user files) and unstructured data (PDF summaries)
    to provide contextual answers for the given question.

    Args:
        question (str): The user’s question.
        token (str, optional): OAuth2 bearer token. Injected via dependency.
        db (Session, optional): Database session. Injected via dependency.

    Returns:
        StreamingResponse: Stream of agent events in SSE format.
    """

    # Get user ID from token
    user_id = get_current_user_id(token)

    # collect filenames and storage URIs
    file_names = [f.file_name for f in file_service.get_files(db=db, user_id=user_id)]
    storage_uris = [
        f.storage_uri for f in file_service.get_files(db=db, user_id=user_id)
    ]

    # Get structured data description for all user files
    structured_data_info = "\n\n".join(
        file.format()
        for file in file_service.get_files_metadata(db=db, user_id=user_id)
    )

    # Summary of unstractured data avaliable to user
    unstructured_data_info = """
*** Available PDF Files ***

- Well Completion Report OzAlpha-1: Detailed completion report for OzAlpha-1 well.
- West Mereenie 28 Well Completion Report: Completion summary and metrics for West Mereenie 28.
- West Mereenie 27 Well Completion Report: Completion summary and metrics for West Mereenie 27.
- Carpentaria-1 BASIC Well Completion Report: Basic completion report for Carpentaria-1.
- Carpentaria-2: 2H BASIC Well Completion Report: Basic completion report for Carpentaria-2 2H.
- Tanumbirini 3H: Tanumbirini 3HST1 BASIC Well Completion Report: Basic completion report for Tanumbirini 3HST1.
"""

    stream = AgentService.stream(
        question=question,
        file_names=file_names,
        structured_data_info=structured_data_info,
        unstructured_data_info=unstructured_data_info,
        storage_uris=storage_uris,
    )

    return StreamingResponse(stream, media_type="text/event-stream")
