"""
...
"""

from fastapi import APIRouter

from schemas.agent import AgentRequest

# from services.agent import AgentService

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/chat")
def chat(agent_request: AgentRequest):
    """..."""
    return {"visualization": None, "message": ""}
