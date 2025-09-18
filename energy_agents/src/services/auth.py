"""
Service layer for authentication.

Handles user login, credential verification, token generation,
and retrieval of the current authenticated user.
"""

from dataclasses import dataclass
from typing import Optional

from pydantic import EmailStr
from sqlalchemy.orm import Session

from core.secutiry import JWTHandler, jwt_handler, Hasher, hasher
from schemas.user import UserInDB, UserRead
from schemas.auth_token import Token
from services.user import UserService


@dataclass
class AuthService:
    """
    Service class for authentication and authorization logic.
    """

    jwt_handler: JWTHandler
    hasher: Hasher

    def authenticate(
        self, db: Session, email: EmailStr, password: str
    ) -> Optional[UserInDB]:
        """Validate user credentials.

        Args:
            db (Session): Active database session.
            email (EmailStr): User email.
            password (str): Plaintext password to verify.

        Returns:
            Optional[UserInDB]: User if authentication succeeds,
            otherwise None.
        """
        user = UserService.get_user_by_email(db=db, email=email)
        if not self.hasher.verify(password, user.password):
            return None
        return user

    def login(self, db: Session, email: str, password: str) -> Token:
        """Authenticate and issue an access token.

        Args:
            db (Session): Active database session.
            email (str): User email.
            password (str): Plaintext password.

        Returns:
            Token: Access token and type for authorization.

        Raises:
            HTTPException: If authentication fails.
        """
        # Verify credentials
        user = self.authenticate(db=db, email=email, password=password)
        if user is None:
            raise self.jwt_handler.credential_exception
        # Generate access token
        access_token = self.jwt_handler.create_access_token(data={"sub": str(user.id)})
        return Token(access_token=access_token, token_type="bearer")

    def get_current_user(self, db: Session, token: str) -> UserRead:
        """Retrieve the currently authenticated user.

        Args:
            db (Session): Active database session.
            token (str): JWT access token.

        Returns:
            UserRead: Authenticated user data.
        """
        # Decode token and fetch user
        token_data = self.jwt_handler.decode_access_token(token=token)
        user = UserService.get_current_user(db=db, id=token_data.user_id)
        return user


# Global authentication service instance configured with JWT and hashing utilitiess
auth_service_ = AuthService(
    jwt_handler=jwt_handler,
    hasher=hasher,
)
