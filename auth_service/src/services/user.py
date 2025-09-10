"""
User service module.

This module defines the `UserService` class, which provides high-level
business logic for user operations. It acts as a bridge between the API
layer and the repository layer, handling tasks such as password hashing,
user validation, and data serialization.

Responsibilities:
    - Fetch users by ID or email with proper error handling.
    - Create new users with hashed passwords.
    - Retrieve the current authenticated user.
"""

from pydantic import EmailStr
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from core.security import hasher
from schemas.user import UserInDB, UserCreate, UserRead
from repositories.user import UserRepository


class UserService:
    """
    Service class for user-related business logic.

    Provides static methods to encapsulate common user operations while
    maintaining separation of concerns from the database layer.
    """

    @staticmethod
    def get_user_by_id(db: Session, id: str) -> UserInDB:
        """
        Retrieve a user by their unique ID with proper validation.

        Args:
            db (Session): SQLAlchemy database session.
            id (str): The unique identifier of the user.

        Raises:
            HTTPException: If the user is not found.

        Returns:
            UserInDB: The user object validated through Pydantic.
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
        Retrieve a user by their email address with proper validation.

        Args:
            db: SQLAlchemy database session.
            email: The email of the user.

        Returns:
            UserInDB: The user object validated through Pydantic.

        Raises:
            HTTPException: If the user is not found.
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
        Create a new user with hashed password and store it in the database.

        Args:
            db: SQLAlchemy database session.
            user: User creation data including plain-text password.

        Returns:
            UserInDB: The newly created user object validated through Pydantic.
        """
        hashed_password = hasher.hash(user.password)
        user_data = user.model_dump()
        user_data["password"] = hashed_password
        db_user = UserRepository.create_user(db=db, user_data=user_data)
        return UserInDB.model_validate(db_user)

    @staticmethod
    def get_current_user(db: Session, id: str) -> UserRead:
        """
        Retrieve the currently authenticated user by ID.

        Args:
            db: SQLAlchemy database session.
            id: The ID of the authenticated user.

        Returns:
            UserRead: The user object suitable for API responses.
        """
        db_user = UserRepository.get_user_by_id(db=db, id=id)
        return UserRead.model_validate(db_user)
