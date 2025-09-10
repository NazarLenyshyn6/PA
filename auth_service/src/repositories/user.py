"""
User repository module.

This module defines the `UserRepository` class, which encapsulates database
operations for the `User` model. It provides an abstraction layer for querying
and persisting user-related data, ensuring separation of concerns between
database logic and business logic.

Responsibilities:
    - Fetching users by ID or email.
    - Creating new users in the database.
"""

from typing import Optional

from pydantic import EmailStr
from sqlalchemy.orm import Session

from models.user import User


class UserRepository:
    """
    Repository class for managing user-related database operations.

    This class provides static methods to interact with the `User` table.
    It ensures that all user database access is encapsulated, making the
    persistence layer reusable and testable.
    """

    @staticmethod
    def get_user_by_id(db: Session, id: str) -> Optional[User]:
        """
        Retrieve a user by their unique ID.

        Args:
            db: SQLAlchemy database session.
            id: Unique identifier of the user.

        Returns:
            Optional[User]: The user object if found, otherwise None.
        """
        user = db.query(User).where(User.id == id).first()
        return user

    @staticmethod
    def get_user_by_email(db: Session, email: EmailStr) -> Optional[User]:
        """
        Retrieve a user by their email address.

        Args:
            db: SQLAlchemy database session.
            email: Email address of the user.

        Returns:
            Optional[User]: The user object if found, otherwise None.
        """
        user = db.query(User).where(User.email == email).first()
        return user

    @staticmethod
    def create_user(db: Session, user_data: dict) -> User:
        """
        Create a new user in the database.

        Args:
            db: SQLAlchemy database session.
            user_data: Dictionary containing user attributes (e.g.,
                email, password).

        Returns:
            User: The newly created user object.
        """
        db_user = User(**user_data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
