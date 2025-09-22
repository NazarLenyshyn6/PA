"""
Authentication API routes.

Provides endpoints for:
- Retrieving the current authenticated user
- User registration
- User login with OAuth2 password flow
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
    """Retrieve the currently authenticated user.

    Args:
        token (str, optional): OAuth2 bearer token. Defaults via dependency injection.
        db (Session, optional): Database session. Defaults via dependency injection.

    Returns:
        UserRead: Authenticated user's information.
    """
    return auth_service_.get_current_user(db=db, token=token)


@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(db_manager.get_db)):
    """Register a new user.

    Args:
        user (UserCreate): User registration data (email and password).
        db (Session, optional): Database session. Defaults via dependency injection.

    Returns:
        UserInDB: Created user information.
    """
    return UserService.create_user(db=db, user=user)


@router.post("/login")
def login(
    user: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(db_manager.get_db),
):
    """Authenticate a user and generate an access token.

    Args:
        user (OAuth2PasswordRequestForm, optional): Form containing username (email) and password.
        db (Session, optional): Database session. Defaults via dependency injection.

    Returns:
        Token: JWT access token and type for authenticated session.
    """
    return auth_service_.login(db=db, email=user.username, password=user.password)
