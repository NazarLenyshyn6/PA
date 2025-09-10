"""
Authentication utilities module.

This module provides utilities for password hashing and JWT-based authentication.
It centralizes secure password handling using `passlib` and token-based
authentication using `python-jose`. It also integrates with the global
application settings for consistency across the codebase.

Components:
    - Hasher: Secure password hashing and verification utility.
    - JWTHandler: JSON Web Token (JWT) creation and validation handler.
"""

from dataclasses import dataclass
from typing_extensions import List, Optional
from datetime import timedelta, datetime

from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status

from core.config import settings
from schemas.auth_token import TokenData


class Hasher:
    """
    Password hashing and verification utility.

    Encapsulates `passlib`'s `CryptContext` for secure password
    hashing and comparison, supporting configurable hashing schemes.

    Attributes:
        _context: The cryptographic context used for hashing
            and verifying passwords.
    """

    def __init__(self, schemes: List[str] = ["bcrypt"], deprecated="auto"):
        """
        Initialize the hasher with a given hashing scheme.

        Args:
            schemes: List of hashing algorithms supported.
                Defaults to ["bcrypt"].
            deprecated: Policy for deprecating old schemes.
                Defaults to "auto".
        """
        self._context = CryptContext(schemes=schemes, deprecated=deprecated)

    def hash(self, password: str) -> str:
        """
        Hash a plain-text password.

        Args:
            password: The plain-text password to be hashed.

        Returns:
            str: The securely hashed password.
        """
        return self._context.hash(password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify whether a plain-text password matches its hashed counterpart.

        Args:
            plain_password: The user-provided password.
            hashed_password: The stored hashed password.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return self._context.verify(plain_password, hashed_password)


@dataclass
class JWTHandler:
    """
    JSON Web Token (JWT) utility for encoding and decoding authentication tokens.

    Provides methods for creating and validating JWT tokens, which are commonly
    used for stateless authentication in APIs.

    Attributes:
        secret_key: The cryptographic secret key for signing tokens.
        algorithm: The algorithm used to sign tokens (e.g., "HS256").
        access_token_expire_minutes: Default expiration duration for access tokens.
    """

    secret_key: str
    algorithm: str
    access_token_expire_minutes: timedelta

    @property
    def credential_exception(self) -> HTTPException:
        """
        Standardized exception for invalid authentication credentials.

        Returns:
            HTTPException: An HTTP 401 exception used when authentication fails.
        """
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    def create_access_token(
        self, data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a signed JWT access token.

        Args:
            data: The claims to include in the token payload.
            expires_delta: Custom expiration period.
                If not provided, defaults to the configured expiration time.

        Returns:
            str: The encoded JWT string.
        """
        to_encode = data.copy()
        expire = datetime.now() + (expires_delta or self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def decode_access_token(self, token: str, key: str = "sub") -> TokenData:
        """
        Decode and validate a JWT access token.

        Args:
            token: The JWT token to decode.
            key: The claim key used to extract the user identifier.
                Defaults to "sub".

        Raises:
            HTTPException: If the token is invalid or expired.

        Returns:
            TokenData: A data object containing the extracted user ID.
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id = payload.get(key)
            if user_id is None:
                raise self.credential_exception
            return TokenData(user_id=user_id)
        except JWTError:
            raise self.credential_exception


# Global instances for password hashing and JWT handling
hasher = Hasher()
jwt_handler = JWTHandler(
    secret_key=settings.security.SECRET_KEY,
    algorithm=settings.security.ALGORITHM,
    access_token_expire_minutes=settings.security.ACCESS_TOKEN_EXPIRE_MINUTES_TIMEDELTA,
)
