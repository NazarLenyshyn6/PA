"""
...
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
    ...
    """
    file_cache.connect_client()
    yield
    file_cache.close_client()


# Initialize FastAPI application with lifespan context
app = FastAPI(lifespan=lifespan)

# Add CORS middleware to allow external clients to access the API
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
    ...
    """
    status_code = exc.response.status_code if exc.response else 400
    detail = exc.response.text if exc.response else str(exc)
    return JSONResponse(status_code=status_code, content={"detail": detail})


# Include API routers
app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8000)
