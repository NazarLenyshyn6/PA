"""
Authentication API routes.

This module defines FastAPI endpoints for user authentication and registration.
It integrates with the `AuthService` and `UserService` to provide secure
authentication using JWTs, user registration, and retrieval of the current
authenticated user.

Endpoints:
    - GET /auth/me: Retrieve the currently authenticated user.
    - POST /auth/register: Register a new user.
    - POST /auth/login: Authenticate a user and obtain an access token.
"""

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from core.db import db_manager
from schemas.user import UserCreate
from services.user import UserService
from services.auth import auth_service_

# OAuth2 password bearer scheme for extracting token from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.get("/me")
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(db_manager.get_db),
):
    """
    Retrieve the currently authenticated user.

    Args:
        token: JWT token extracted from the Authorization header.
        db: SQLAlchemy database session dependency.

    Raises:
        HTTPException: If the token is invalid or the user does not exist.

    Returns:
        UserRead: Data of the currently authenticated user.
    """
    return auth_service_.get_current_user(db=db, token=token)


@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(db_manager.get_db)):
    """
    Register a new user in the system.

    Args:
        user: Incoming user registration data.
        db: SQLAlchemy database session dependency.

    Returns:
        UserInDB: The newly created user object (internal representation).
    """
    return UserService.create_user(db=db, user=user)


@router.post("/login")
def login(
    user: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(db_manager.get_db),
):
    """
    Authenticate a user and return a JWT access token.

    Args:
        user: Form data containing username (email)
            and password.
        db: SQLAlchemy database session dependency.

    Raises:
        HTTPException: If authentication fails.

    Returns:
        Token: JWT access token object containing the access token and type.
    """
    return auth_service_.login(db=db, email=user.username, password=user.password)
