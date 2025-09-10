"""
FastAPI application entry point.

This module initializes the FastAPI application, sets up database tables,
and includes API routers. It serves as the main entry point for running
the application server.

Responsibilities:
    - Initialize the FastAPI app.
    - Create database tables using SQLAlchemy Base metadata.
    - Include API routers for versioned endpoints.
    - Run the application via Uvicorn in development mode.
"""

import uvicorn
from fastapi import FastAPI

from api.v1.router import api_router
from core.db import db_manager
from models.base import Base

# Create all database tables defined in SQLAlchemy Base metadata
Base.metadata.create_all(bind=db_manager.engine)

# Initialize FastAPI application
app = FastAPI()

# Include versioned API router
app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8000)
