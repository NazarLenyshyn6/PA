"""
Repository layer for file database operations.

Provides methods to create, retrieve, and delete File records.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from core.exceptions import DuplicateFileNameError
from schemas.file import FileCreate
from models.file import File


class FileRepository:
    """Repository for performing CRUD operations on File entities."""

    @classmethod
    def create_file(cls, db: Session, file_data: FileCreate) -> File:
        """Create a new file record in the database.

        Args:
            db (Session): Active database session.
            file_data (FileCreate): Data for the new file.

        Raises:
            DuplicateFileNameError: If a file with the same name exists for the user.

        Returns:
            File: Newly created File instance.
        """
        db_existing_file = cls.get_file(
            db=db, user_id=file_data.user_id, file_name=file_data.file_name
        )
        if db_existing_file:
            raise DuplicateFileNameError("File with this name already exists.")
        db_file = File(**file_data.model_dump())
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        return db_file

    @classmethod
    def get_files(cls, db: Session, user_id: int) -> List[File]:
        """Retrieve all files for a specific user.

        Args:
            db (Session): Active database session.
            user_id (int): ID of the user.

        Returns:
            List[File]: List of File instances for the user.
        """
        files = db.query(File).filter(File.user_id == user_id).all()
        return files

    @classmethod
    def get_file(cls, db: Session, user_id: int, file_name: str) -> Optional[File]:
        """Retrieve a specific file for a user by name.

        Args:
            db (Session): Active database session.
            user_id (int): ID of the user.
            file_name (str): Name of the file.

        Returns:
            Optional[File]: File instance if found, else None.
        """
        file = (
            db.query(File)
            .filter(File.user_id == user_id, File.file_name == file_name)
            .first()
        )
        return file

    @classmethod
    def delete_file(cls, db: Session, user_id: int, file_name: str) -> None:
        """Delete a file record from the database.

        Args:
            db (Session): Active database session.
            user_id (int): ID of the user.
            file_name (str): Name of the file to delete.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        db_file = cls.get_file(db=db, user_id=user_id, file_name=file_name)
        if db_file is None:
            raise FileNotFoundError(
                f"No file found with name '{file_name}' for user_id={user_id}"
            )
        db.delete(db_file)
        db.commit()
