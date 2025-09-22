"""
Repository layer for user database operations.

Provides methods to query and persist User records.
"""

from typing import Optional

from pydantic import EmailStr
from sqlalchemy.orm import Session

from models.user import User


class UserRepository:
    """
    Repository for performing CRUD operations on User entities.
    """

    @staticmethod
    def get_user_by_id(db: Session, id: str) -> Optional[User]:
        """Retrieve a user by their ID.

        Args:
            db (Session): Active database session.
            id (str): User identifier.

        Returns:
            Optional[User]: User instance if found, else None.
        """
        user = db.query(User).where(User.id == id).first()
        return user

    @staticmethod
    def get_user_by_email(db: Session, email: EmailStr) -> Optional[User]:
        """Retrieve a user by their email address.

        Args:
            db (Session): Active database session.
            email (EmailStr): User email.

        Returns:
            Optional[User]: User instance if found, else None.
        """
        user = db.query(User).where(User.email == email).first()
        return user

    @staticmethod
    def create_user(db: Session, user_data: dict) -> User:
        """Create and persist a new user in the database.

        Args:
            db (Session): Active database session.
            user_data (dict): Dictionary containing user fields.

        Returns:
            User: Newly created User instance.
        """
        db_user = User(**user_data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
