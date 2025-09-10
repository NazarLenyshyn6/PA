"""
JWT authentication handler module.

This module provides utilities for encoding, decoding, and validating
JWT access tokens in the application. It integrates with FastAPI's security
dependencies to extract and validate tokens from incoming requests.

Components:
    - JWTHandler: Dataclass encapsulating JWT decoding and validation logic.
    - get_current_user_id: FastAPI dependency to retrieve the current user's ID from a token.
    - security: HTTPBearer instance for token extraction.
"""

from dataclasses import dataclass
from datetime import timedelta

from jose import JWTError, jwt
from fastapi import HTTPException, status, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.config import settings

# FastAPI HTTPBearer security scheme for extracting Authorization headers
security = HTTPBearer()


@dataclass
class JWTHandler:
    """
    Handler for JWT token operations.

    Attributes:
        secret_key: Secret key for signing and verifying JWT tokens.
        algorithm: Algorithm used for encoding and decoding tokens.
        access_token_expire_minutes: Token expiration duration.
    """

    secret_key: str
    algorithm: str
    access_token_expire_minutes: timedelta

    def decode_access_token(self, token: str, key: str = "sub") -> int:
        """
        Decode a JWT token and extract the user ID.

        Args:
            token: JWT access token string.
            key: Claim key containing the user identifier. Defaults to "sub".

        Raises:
            HTTPException: If the token is invalid or the user ID claim is missing.

        Returns:
            int: User ID extracted from the token.
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id = payload.get(key)
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: user_id missing",
                )
            return int(user_id)
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )


# Global JWT handler instance configured with app security settings
jwt_handler = JWTHandler(
    secret_key=settings.security.SECRET_KEY,
    algorithm=settings.security.ALGORITHM,
    access_token_expire_minutes=settings.security.ACCESS_TOKEN_EXPIRE_MINUTES_TIMEDELTA,
)


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> int:
    """
    FastAPI dependency to retrieve the current authenticated user's ID.

    Extracts the JWT token from the Authorization header and decodes it
    using the global JWTHandler instance.

    Args:
        credentials (HTTPAuthorizationCredentials): Automatically provided
            by FastAPI's Security dependency.

    Raises:
        HTTPException: If token validation fails.

    Returns:
        int: ID of the authenticated user.
    """
    token = credentials.credentials
    return jwt_handler.decode_access_token(token=token)
