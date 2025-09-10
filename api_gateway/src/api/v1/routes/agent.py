"""
Chat and agent interaction API routes.

This module provides endpoints for real-time streaming of agent responses,
retrieving conversation history, and persisting chat history. It integrates
with `AgentClient` for agent interactions, `FileClient` for active file
management, and `SessionClient` for session handling. OAuth2 token
authentication is required for all endpoints.

Endpoints:
    GET /chat/stream: Stream agent responses in real time for a given question.
    GET /chat/history: Retrieve conversation history for the current session and file.
    POST /chat/save: Persist the conversation memory to the database.
"""

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import StreamingResponse

from clients.session import SessionClient
from clients.file import FileClient
from clients.agent import AgentClient
from core.security import get_current_user_id

# OAuth2 dependency for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/gateway/auth/login")

router = APIRouter(prefix="/chat", tags=["Chat"])


# Todo
# @router.get("/stream")
# async def stream(
#     question: str,
#     token: str = Depends(oauth2_scheme),
# ):
#     """
#     Stream agent responses in real-time for a given question.

#     Args:
#         question: User's question to the agent.
#         token: OAuth2 bearer token injected via dependency.

#     Returns:
#         StreamingResponse: Streaming text response from the agent.
#     """
#     # Get user ID from token
#     user_id = get_current_user_id(token)

#     # Get currently active session ID
#     session_id = SessionClient.get_active_session_id(token=token)

#     # Get currently active file for the session
#     active_file = FileClient.get_active_file(token=token, session=session_id)

#     # Call async streaming method of your client
#     stream = AgentClient.stream(
#         question=question,
#         user_id=user_id,
#         session_id=session_id,
#         file_name=active_file["file_name"],
#         storage_uri=active_file["storage_uri"],
#         dataset_summary=active_file["summary"],
#     )

#     # Return StreamingResponse with media_type text/plain for real-time streaming
#     return StreamingResponse(stream, media_type="text/event-stream")


# Todo
# @router.get("/history")
# def get_conversation_memory(token: str = Depends(oauth2_scheme)):
#     """
#     Retrieve the conversation memory for the current user session and active file.

#     Args:
#         token: OAuth2 bearer token injected via dependency.

#     Returns:
#         dict: Conversation memory retrieved from AgentClient.
#     """

#     # Get user ID from token
#     user_id = get_current_user_id(token)

#     # Get currently active session ID
#     session_id = SessionClient.get_active_session_id(token=token)

#     # Get currently active file for the session
#     active_file = FileClient.get_active_file(token=token, session=session_id)

#     # Retrieve conversation memory via AgentClient
#     response = AgentClient.get_conversation_memory(
#         user_id=user_id,
#         session_id=session_id,
#         file_name=active_file["file_name"],
#         storage_uri=active_file["storage_uri"],
#     )
#     return response


@router.post("/save")
def save_memory(
    token: str = Depends(oauth2_scheme),
):
    """
    Persist the current conversation memory to the database.

    Args:
        token: OAuth2 bearer token injected via dependency.

    Returns:
        None
    """

    # Get user ID from token
    user_id = get_current_user_id(token)

    # Get currently active session ID
    session_id = SessionClient.get_active_session_id(token=token)

    # Get currently active file for the session
    active_file = FileClient.get_active_file(token=token, session=session_id)

    # Save conversation memory using AgentClient
    AgentClient.save_memory(
        user_id=user_id, session_id=session_id, file_name=active_file["file_name"]
    )
