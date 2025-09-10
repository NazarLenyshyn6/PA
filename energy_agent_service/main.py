"""
Main application entry point for the FastAPI agent memory service.

This module initializes the FastAPI application, sets up the database
tables, manages the memory cache lifecycle, and mounts API routers.

Features:
    - Database initialization using SQLAlchemy `Base.metadata.create_all`.
    - Lifecycle management for the memory cache client.
    - Integration of versioned API router (`api_router`).
    - Runs the app using Uvicorn when executed as the main module.
"""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from api.v1.router import api_router
from core.db import db_manager

from cache.memory import memory_cache_manager
from models.base import Base

# Create all database tables if they do not exist
Base.metadata.create_all(bind=db_manager.engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app.

    Handles setup and teardown for application-level resources, such
    as connecting and disconnecting the memory cache client.

    Args:
        app (FastAPI): The FastAPI application instance.

    Yields:
        None
    """
    # Connect the memory cache client when app starts
    memory_cache_manager.connect_client()

    yield

    # Close the memory cache client when app shuts down
    memory_cache_manager.close_client()


# Initialize FastAPI application with lifespan context manager
app = FastAPI(lifespan=lifespan)

# Include the versioned API router
app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8005)
