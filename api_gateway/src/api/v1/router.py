"""
API Gateway router for version 1.

This module aggregates and exposes all submodule routers under a single
API gateway prefix. It acts as the central entry point for v1 endpoints,
including authentication, session management, file operations, and chat.

Included Routers:
    - Auth: Handles user authentication and authorization endpoints.
    - Session: Manages user sessions (create, delete, list, active).
    - File: Handles file management (upload, list, active, delete).
    - Agent: Handles agent chat and conversation endpoints.
"""

from fastapi import APIRouter

from api.v1.routes.auth import router as auth_router
from api.v1.routes.session import router as session_router
from api.v1.routes.file import router as file_router

# from api.v1.routes.agent import router as energy_agents_router

# Create main API router for v1 gateway
api_router = APIRouter(prefix="/api/v1/gateway")

api_router.include_router(auth_router)  # Auth endpoints
api_router.include_router(session_router)  # Session endpoints
api_router.include_router(file_router)  # File endpoints
# api_router.include_router(agent_router)  # Energy Agents endpoints
