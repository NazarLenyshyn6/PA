"""
Service layer for user management.

Provides methods for retrieving, creating, and validating users,
wrapping repository operations with additional business logic.
"""

from pydantic import EmailStr
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from core.secutiry import hasher
from schemas.user import UserInDB, UserCreate, UserRead
from repositories.user import UserRepository


class UserService:
    """
    Service class for handling user-related operations.
    """

    @staticmethod
    def get_user_by_id(db: Session, id: str) -> UserInDB:
        """Retrieve a user by their ID.

        Args:
            db (Session): Active database session.
            id (str): User identifier.

        Returns:
            UserInDB: User object from the database.

        Raises:
            HTTPException: If the user does not exist.
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
        """Retrieve a user by their email address.

        Args:
            db (Session): Active database session.
            email (EmailStr): User email.

        Returns:
            UserInDB: User object from the database.

        Raises:
            HTTPException: If the user does not exist.
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
        """Create a new user with hashed password.

        Args:
            db (Session): Active database session.
            user (UserCreate): User input data.

        Returns:
            UserInDB: Created user object.
        """
        # Hash the provided password before storing
        hashed_password = hasher.hash(user.password)

        # Replace plain password with hashed version
        user_data = user.model_dump()
        user_data["password"] = hashed_password

        # Persist user in database
        db_user = UserRepository.create_user(db=db, user_data=user_data)
        return UserInDB.model_validate(db_user)

    @staticmethod
    def get_current_user(db: Session, id: str) -> UserRead:
        """Retrieve the current authenticated user.

        Args:
            db (Session): Active database session.
            id (str): User identifier.

        Returns:
            UserRead: User data in a safe response schema.
        """
        db_user = UserRepository.get_user_by_id(db=db, id=id)
        return UserRead.model_validate(db_user)
