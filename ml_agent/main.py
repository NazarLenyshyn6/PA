"""
This module initializes and runs the FastAPI application for the agent service.
It configures CORS middleware and includes the versioned API router.

The application can be started directly with:
    python main.py
or with uvicorn:
    uvicorn main:app --reload --port 8001
"""

import uvicorn
from fastapi import FastAPI

from api.agent import router


# Initialize the FastAPI application
app = FastAPI()


# Include the versioned API router
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8001)
