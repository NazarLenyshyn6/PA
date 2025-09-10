"""
FastAPI application entry point.

This module initializes the FastAPI application, configures
the lifespan for connecting and disconnecting the file cache,
and includes the API version 1 router. It also ensures that
all database models are created before the app starts.

The application can be run directly using Uvicorn.
"""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from api.v1.router import api_router
from core.db import db_manager
from cache.file import file_cache
from models.base import Base

# Create all database tables on startup
Base.metadata.create_all(bind=db_manager.engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.

    Connects to the file cache when the application starts
    and closes the connection when the application shuts down.

    Args:
        app: FastAPI application instance.

    Yields:
        None
    """
    file_cache.connect_client()
    yield
    file_cache.close_client()


# Initialize FastAPI application with the lifespan manager
app = FastAPI(lifespan=lifespan)

# Include all API v1 routes
app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8002)
