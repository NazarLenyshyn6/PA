"""
Authentication API routes.

This module provides endpoints for user authentication and registration
using FastAPI and OAuth2. It leverages the `AuthClient` to interact with
the authentication backend service.

Endpoints:
    GET /auth/me: Retrieve the current authenticated user's information.
    POST /auth/register: Register a new user.
    POST /auth/login: Authenticate a user and obtain an access token.
"""

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from schemas.auth import RegisterRequest
from clients.auth import AuthClient

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/gateway/auth/login")

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/me")
def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Retrieve the current authenticated user's information.

    This endpoint uses the OAuth2 bearer token to identify the user
    and fetch user details from the Auth service.

    Args:
        token: Bearer token injected by FastAPI dependency.

    Returns:
        dict: User information retrieved from AuthClient.
    """
    return AuthClient.get_current_user(token=token)


@router.post("/register")
def register_user(register_request: RegisterRequest):
    """
    Register a new user with email and password.

    Args:
        register_request: Pydantic model containing
            email and password fields.

    Returns:
        dict: Response from AuthClient confirming registration.
    """
    return AuthClient.register_user(
        email=register_request.email, password=register_request.password
    )


@router.post("/login")
def login(
    user: OAuth2PasswordRequestForm = Depends(),
):
    """
    Authenticate a user and obtain an access token.

    Args:
        user: FastAPI form dependency containing
            username (email) and password.

    Returns:
        dict: Authentication token and related user info from AuthClient.
    """
    return AuthClient.login(email=user.username, password=user.password)
