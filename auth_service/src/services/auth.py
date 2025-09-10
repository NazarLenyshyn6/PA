"""
Authentication service module.

This module defines the `AuthService` class, which encapsulates the core
authentication logic for the application. It integrates with the user
service, hashing utilities, and JWT handler to provide secure
authentication, login, and user retrieval.

Responsibilities:
    - Authenticating users via email and password.
    - Generating and returning JWT access tokens upon login.
    - Retrieving the currently authenticated user from a token.
"""

from dataclasses import dataclass
from typing import Optional

from pydantic import EmailStr
from sqlalchemy.orm import Session

from core.security import JWTHandler, jwt_handler, Hasher, hasher
from schemas.user import UserInDB, UserRead
from schemas.auth_token import Token
from services.user import UserService


@dataclass
class AuthService:
    """
    Service class for handling authentication logic.

    This service orchestrates authentication by verifying user credentials,
    issuing JWT tokens, and resolving authenticated users from tokens.

    Attributes:
        jwt_handler (JWTHandler): Utility for encoding and decoding JWT tokens.
        hasher (Hasher): Utility for hashing and verifying user passwords.
    """

    jwt_handler: JWTHandler
    hasher: Hasher

    def authenticate(
        self, db: Session, email: EmailStr, password: str
    ) -> Optional[UserInDB]:
        """
        Authenticate a user by verifying their email and password.

        Args:
            db: SQLAlchemy database session.
            email: The user's email address.
            password: The user's plain-text password.

        Returns:
            Optional[UserInDB]: The user object if authentication succeeds,
            otherwise None.
        """
        user = UserService.get_user_by_email(db=db, email=email)
        if not self.hasher.verify(password, user.password):
            return None
        return user

    def login(self, db: Session, email: str, password: str) -> Token:
        """
        Authenticate a user and issue a JWT access token.

        Args:
            db: SQLAlchemy database session.
            email: The user's email address.
            password: The user's plain-text password.

        Raises:
            HTTPException: If authentication fails, an HTTP 401 error is raised.

        Returns:
            Token: A JWT token object containing the access token and its type.
        """
        user = self.authenticate(db=db, email=email, password=password)
        if user is None:
            raise self.jwt_handler.credential_exception
        access_token = self.jwt_handler.create_access_token(data={"sub": str(user.id)})
        return Token(access_token=access_token, token_type="bearer")

    def get_current_user(self, db: Session, token: str) -> UserRead:
        """
        Retrieve the currently authenticated user from a JWT access token.

        Args:
            db: SQLAlchemy database session.
            token: JWT token provided by the client.

        Raises:
            HTTPException: If the token is invalid or the user does not exist.

        Returns:
            UserRead: The authenticated user's data.
        """
        token_data = self.jwt_handler.decode_access_token(token=token)
        user = UserService.get_current_user(db=db, id=token_data.user_id)
        return user


# Global authentication service instance configured with JWT and hashing utilities
auth_service_ = AuthService(
    jwt_handler=jwt_handler,
    hasher=hasher,
)
