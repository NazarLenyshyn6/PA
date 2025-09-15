""" """

from dataclasses import dataclass
from typing_extensions import List, Optional
from datetime import timedelta, datetime

from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from core.config import settings
from schemas.auth_token import TokenData


security = HTTPBearer()


class Hasher:
    """
    ...
    """

    def __init__(self, schemes: List[str] = ["bcrypt"], deprecated="auto"):
        """
        ....
        """
        self._context = CryptContext(schemes=schemes, deprecated=deprecated)

    def hash(self, password: str) -> str:
        """
        ...
        """
        return self._context.hash(password)

    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """
        ...
        """
        return self._context.verify(plain_password, hashed_password)


@dataclass
class JWTHandler:
    """
    ...
    """

    secret_key: str
    algorithm: str
    access_token_expire_minutes: timedelta

    @property
    def credential_exception(self) -> HTTPException:
        """
        ...
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
        ...
        """
        to_encode = data.copy()
        expire = datetime.now() + (expires_delta or self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def decode_access_token(self, token: str, key: str = "sub") -> TokenData:
        """
        ...
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id = payload.get(key)
            if user_id is None:
                raise self.credential_exception
            return TokenData(user_id=user_id)
        except JWTError:
            raise self.credential_exception


hasher = Hasher()
jwt_handler = JWTHandler(
    secret_key=settings.security.SECRET_KEY,
    algorithm=settings.security.ALGORITHM,
    access_token_expire_minutes=settings.security.ACCESS_TOKEN_EXPIRE_MINUTES_TIMEDELTA,
)


def get_current_user_id(token: str) -> int:
    """
    ...
    """
    return int(jwt_handler.decode_access_token(token=token).user_id)
