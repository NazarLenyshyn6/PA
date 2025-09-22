"""
Main application entrypoint for the FastAPI service.

This module configures the database, cache client, middleware,
exception handling, and API routing for the application.
"""

from contextlib import asynccontextmanager

import uvicorn
from requests.exceptions import HTTPError
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.v1.router import api_router
from core.db import db_manager
from cache.file import file_cache
from models.base import Base

# Create all database tables
Base.metadata.create_all(bind=db_manager.engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifespan by connecting and closing cache client.

    Args:
        app (FastAPI): The FastAPI application instance.
    """
    file_cache.connect_client()
    yield
    file_cache.close_client()


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPError)
async def http_error_handler(request: Request, exc: HTTPError):
    """
    Handle HTTP errors raised by requests library.

        Args:
            request (Request): The incoming request that triggered the exception.
            exc (HTTPError): The raised HTTP error.

        Returns:
            JSONResponse: Response with status code and error details.
    """
    status_code = exc.response.status_code if exc.response else 400
    detail = exc.response.text if exc.response else str(exc)
    return JSONResponse(status_code=status_code, content={"detail": detail})


app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8000)
