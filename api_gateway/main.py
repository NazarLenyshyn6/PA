"""
Main entrypoint for the FastAPI application.

This module initializes the FastAPI app, configures CORS middleware,
sets up custom exception handling, and registers API routers.
It also provides the `__main__` block for running the app with Uvicorn.

Key responsibilities:
- Configure cross-origin requests (CORS) for external access.
- Handle `requests.exceptions.HTTPError` exceptions gracefully and return JSON responses.
- Mount versioned API routers from the `api.v1.router` module.
- Run the application on port 8003 when executed directly.

"""

import uvicorn
from requests.exceptions import HTTPError
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse


from api.v1.router import api_router

# Initialize the FastAPI application
app = FastAPI()

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
    Custom exception handler for HTTPError raised by the `requests` library.

    Ensures external API errors are returned as valid JSON responses
    with an appropriate HTTP status code and detail message.
    """
    status_code = exc.response.status_code if exc.response else 400
    detail = exc.response.text if exc.response else str(exc)
    return JSONResponse(status_code=status_code, content={"detail": detail})


# Include the API routes from versioned router
app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, port=8003)
