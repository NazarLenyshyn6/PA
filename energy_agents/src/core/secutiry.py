"""
Password hashing and JWT authentication utilities.

Provides classes for secure password hashing and verification,
JWT token creation and decoding, and FastAPI security integration.
"""

from dataclasses import dataclass
from typing_extensions import List, Optional
from datetime import timedelta, datetime

from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.config import settings
from schemas.auth_token import TokenData

# FastAPI security scheme for HTTP Bearer authentication
security = HTTPBearer()


class Hasher:
    """Utility class for password hashing and verification."""

    def __init__(self, schemes: List[str] = ["bcrypt"], deprecated="auto"):
        """Initialize a CryptContext for hashing.

        Args:
            schemes (List[str], optional): List of hashing schemes. Defaults to ["bcrypt"].
            deprecated (str, optional): Policy for deprecated schemes. Defaults to "auto".
        """
        self._context = CryptContext(schemes=schemes, deprecated=deprecated)

    def hash(self, password: str) -> str:
        """Hash a plaintext password.

        Args:
            password (str): Plaintext password.

        Returns:
            str: Hashed password.
        """
        return self._context.hash(password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plaintext password against a hashed password.

        Args:
            plain_password (str): Plaintext password.
            hashed_password (str): Previously hashed password.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return self._context.verify(plain_password, hashed_password)


@dataclass
class JWTHandler:
    """Handler for creating and decoding JWT access tokens."""

    secret_key: str
    algorithm: str
    access_token_expire_minutes: timedelta

    @property
    def credential_exception(self) -> HTTPException:
        """HTTP exception for invalid credentials.

        Returns:
            HTTPException: 401 Unauthorized response.
        """
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a JWT access token.

        Args:
            data (dict): Data to encode in the token (e.g., user ID).
            expires_delta (Optional[timedelta], optional): Custom expiration. Defaults to None.

        Returns:
            str: Encoded JWT token.
        """
        to_encode = data.copy()
        expire = datetime.now() + (expires_delta or self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def decode_access_token(self, token: str, key: str = "sub") -> TokenData:
        """Decode a JWT access token and extract user information.

        Args:
            token (str): JWT token string.
            key (str, optional): Key to extract from token payload. Defaults to "sub".

        Raises:
            HTTPException: If the token is invalid or the key is missing.

        Returns:
            TokenData: Decoded token data containing user_id.
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id = payload.get(key)
            if user_id is None:
                raise self.credential_exception
            return TokenData(user_id=user_id)
        except JWTError:
            raise self.credential_exception


# Global instances for hashing and JWT handling
hasher = Hasher()
jwt_handler = JWTHandler(
    secret_key=settings.security.SECRET_KEY,
    algorithm=settings.security.ALGORITHM,
    access_token_expire_minutes=settings.security.ACCESS_TOKEN_EXPIRE_MINUTES_TIMEDELTA,
)


def get_current_user_id(token: str) -> int:
    """Extract the user ID from a JWT token.

    Args:
        token (str): JWT access token.

    Returns:
        int: User ID extracted from the token.
    """
    return int(jwt_handler.decode_access_token(token=token).user_id)
