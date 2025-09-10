"""
API router module.

This module defines the top-level API router for version 1 (v1) of the API.
It aggregates all route submodules, including the session routes, under the
common prefix '/api/v1'.
"""

from fastapi import APIRouter

from api.v1.routes.session import router as session_router

# Create top-level API router for version 1
api_router = APIRouter(prefix="/api/v1")

# Include session routes
api_router.include_router(session_router)
