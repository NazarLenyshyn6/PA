"""
...
"""

from dataclasses import dataclass
from typing import Optional

from pydantic import EmailStr
from sqlalchemy.orm import Session

from core.security import JWTHandler, jwt_handler, Hasher, hasher
from schemas.auth.user import UserInDB, UserRead
from schemas.auth.auth_token import Token
from services.auth.user import UserService


@dataclass
class AuthService:
    """
    ...
    """

    jwt_handler: JWTHandler
    hasher: Hasher

    def authenticate(
        self, db: Session, email: EmailStr, password: str
    ) -> Optional[UserInDB]:
        """
        ...
        """
        user = UserService.get_user_by_email(db=db, email=email)
        if not self.hasher.verify(password, user.password):
            return None
        return user

    def login(self, db: Session, email: str, password: str) -> Token:
        """
        ...
        """
        user = self.authenticate(db=db, email=email, password=password)
        if user is None:
            raise self.jwt_handler.credential_exception
        access_token = self.jwt_handler.create_access_token(data={"sub": str(user.id)})
        return Token(access_token=access_token, token_type="bearer")

    def get_current_user(self, db: Session, token: str) -> UserRead:
        """
        ...
        """
        token_data = self.jwt_handler.decode_access_token(token=token)
        user = UserService.get_current_user(db=db, id=token_data.user_id)
        return user


# Global authentication service instance configured with JWT and hashing utilities
auth_service_ = AuthService(
    jwt_handler=jwt_handler,
    hasher=hasher,
)
