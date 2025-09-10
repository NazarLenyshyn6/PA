"""
Main application entry point for the FastAPI server.

This module sets up the FastAPI application, initializes the database models,
connects the session cache, and includes the API routers for versioned endpoints.
It also defines the application's lifespan for startup and shutdown tasks.

The application can be started directly using Uvicorn.

Components:
    - Database initialization using SQLAlchemy models.
    - Redis session cache connection management.
    - API routing via `api_router`.
    - Lifespan context for startup and shutdown operations.
"""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from api.v1.router import api_router
from core.db import db_manager
from cache.session import session_cache
from models.base import Base

# Create all database tables
Base.metadata.create_all(bind=db_manager.engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Async context manager for the application's lifespan.

    Connects to the session cache on startup and closes it on shutdown.

    Args:
        app: The FastAPI application instance.

    Yields:
        None
    """
    session_cache.connect_client()
    yield
    session_cache.close_client()


# Initialize FastAPI application with lifespan context
app = FastAPI(lifespan=lifespan)

# Include API routers
app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8001)
