"""
...
"""

from fastapi import APIRouter

from api.v1.routes.auth import router as auth_router
from api.v1.routes.file import router as file_router
from api.v1.routes.agent import router as agent_router

# Main API router for version 1
api_router = APIRouter(prefix="/api/v1")

# Include authentication routes under /api/v1/auth
api_router.include_router(auth_router)
api_router.include_router(file_router)
api_router.include_router(agent_router)
