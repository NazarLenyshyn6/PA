"""
API Router Module.

This module consolidates all version 1 (v1) API routes into a single
FastAPI `APIRouter` instance, which can then be mounted on the main
FastAPI application.
"""

from fastapi import APIRouter

# from api.v1.routes.agent import router as agent_router
from api.v1.routes.memory import router as memory_router

# from api.v1.routes.agent import router as agent_router

# Create a main API router for version 1 of the API
api_router = APIRouter(prefix="/api/v1")

# Include agent-related routes under /api/v1
# api_router.include_router(agent_router)

# Include memory-related routes under /api/v1
api_router.include_router(memory_router)
