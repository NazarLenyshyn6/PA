"""
...
"""

import uvicorn
from fastapi import FastAPI

from src.api.agent import router


# Initialize the FastAPI application
app = FastAPI()

# Include the versioned API router
app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8001)
