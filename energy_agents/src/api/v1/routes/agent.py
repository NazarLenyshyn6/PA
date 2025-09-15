"""
...
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
    """
    ...
    """

    # Get user ID from token
    user_id = get_current_user_id(token)

    # get files descirptions
    structured_data_info = "\n\n".join(
        str(file) for file in file_service.get_files_metadata(db=db, user_id=user_id)
    )

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
        structured_data_info=structured_data_info,
        unstructured_data_info=unstructured_data_info,
    )

    return StreamingResponse(stream, media_type="text/event-stream")
