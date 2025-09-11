"""
...
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from schemas.agent import AgentRequest
from services.agent import AgentService


# Router configuration for agent-related endpoints
router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/stream")
async def stream(
    agent_request: AgentRequest,
):
    """
    Stream responses from the AI agent.

    This endpoint accepts a user question, forwards it to the agent service,
    and streams back responses in real-time using Server-Sent Events (SSE).

    Args:
        agent_request (AgentRequest):
            The validated request body containing the user's question.

    Returns:
        StreamingResponse:
            A stream of events where each event is JSON-encoded.
            Possible event types:
            - {"type": "text", "data": <streamed text>}
            - {"type": "image", "data": <base64 image>}
    """
    stream = AgentService.stream(
        question=agent_request.question, data=agent_request.data
    )

    return StreamingResponse(stream, media_type="text/event-stream")
