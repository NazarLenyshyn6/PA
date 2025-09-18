"""
This module initializes the FastAPI app, includes the API router, and runs
the application server when executed directly.
"""

import uvicorn
from fastapi import FastAPI

from api.agent import router

app = FastAPI()

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8001)
