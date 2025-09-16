"""
...
"""

from fastapi import APIRouter

from schemas.agent import AgentRequest
from services.agent import AgentService

# from services.agent import AgentService

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/chat")
def chat(agent_request: AgentRequest):
    """..."""
    agent_response = AgentService.chat(
        question=agent_request.question,
        file_names=agent_request.file_names,  # Names of avaliable files to store in hash map durint exec()
        data_summaries=agent_request.data_summaries,  # Summarie of the files so agent now for which columns to generate code
        data=agent_request.data,  # List of base64 encoded dataframes
    )
    return {
        "visualization": agent_response["visualization"],
        "analysis_report": agent_response["analysis_report"],
    }
