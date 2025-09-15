"""
...
"""

from typing import Optional

from pydantic import EmailStr
from sqlalchemy.orm import Session

from models.user import User


class UserRepository:
    """
    ...
    """

    @staticmethod
    def get_user_by_id(db: Session, id: str) -> Optional[User]:
        """
        ...
        """
        user = db.query(User).where(User.id == id).first()
        return user

    @staticmethod
    def get_user_by_email(db: Session, email: EmailStr) -> Optional[User]:
        """
        ...
        """
        user = db.query(User).where(User.email == email).first()
        return user

    @staticmethod
    def create_user(db: Session, user_data: dict) -> User:
        """
        ...
        """
        db_user = User(**user_data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
