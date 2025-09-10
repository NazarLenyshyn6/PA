"""
API router module.

This module defines the main FastAPI router for version 1 of the API.
It centralizes all route registrations for the API, making it easy to
include additional routers in the future while keeping a consistent
prefix for versioning.

Currently included routers:
    - Auth routes (`/api/v1/auth`)
"""

from fastapi import APIRouter

from api.v1.routes.auth import router as auth_router

# Main API router for version 1
api_router = APIRouter(prefix="/api/v1")

# Include authentication routes under /api/v1/auth
api_router.include_router(auth_router)
