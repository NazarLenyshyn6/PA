"""
...
"""

from pydantic import EmailStr
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from core.security import hasher
from schemas.auth.user import UserInDB, UserCreate, UserRead
from repositories.auth.user import UserRepository


class UserService:
    """
    ...
    """

    @staticmethod
    def get_user_by_id(db: Session, id: str) -> UserInDB:
        """
        ...
        """
        db_user = UserRepository.get_user_by_id(db=db, id=id)
        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User not found by id {id}",
            )
        return UserInDB.model_validate(db_user)

    @staticmethod
    def get_user_by_email(db: Session, email: EmailStr) -> UserInDB:
        """
        ...
        """
        db_user = UserRepository.get_user_by_email(db=db, email=email)
        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User not found by email {email}",
            )
        return UserInDB.model_validate(db_user)

    @staticmethod
    def create_user(db: Session, user: UserCreate) -> UserInDB:
        """
        ...
        """
        hashed_password = hasher.hash(user.password)
        user_data = user.model_dump()
        user_data["password"] = hashed_password
        db_user = UserRepository.create_user(db=db, user_data=user_data)
        return UserInDB.model_validate(db_user)

    @staticmethod
    def get_current_user(db: Session, id: str) -> UserRead:
        """
        ...
        """
        db_user = UserRepository.get_user_by_id(db=db, id=id)
        return UserRead.model_validate(db_user)
