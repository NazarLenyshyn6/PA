"""
API router module.

This module defines the main FastAPI router for version 1 of the API.
It centralizes all route registrations for the API, making it easy to
include additional routers in the future while keeping a consistent
prefix for versioning.

"""

from fastapi import APIRouter

from api.v1.routes.file import router as file_router

# Main API router for version 1
api_router = APIRouter(prefix="/api/v1")

# Include file routes
api_router.include_router(file_router)
