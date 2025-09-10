"""
Repository for file-related database operations.

This module defines the `FileRepository` class which provides
methods to interact with the database for file management,
including creating, retrieving, and deleting file records.

It enforces uniqueness constraints, handles exceptions, and
ensures proper session commits.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from core.exceptions import DuplicateFileNameError
from schemas.file import FileCreate
from models.file import File


class FileRepository:
    """
    Repository class for performing CRUD operations on `File` records.

    All methods are classmethods to allow stateless usage without
    requiring an instance.
    """

    @classmethod
    def create_file(cls, db: Session, file_data: FileCreate) -> File:
        """
        Create a new file record in the database.

        Ensures that a file with the same name does not already exist
        for the user.

        Args:
            db: SQLAlchemy Session object.
            file_data: Pydantic schema containing file creation data.

        Raises:
            DuplicateFileNameError: If a file with the same name exists.

        Returns:
            File: The newly created SQLAlchemy File model instance.
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
        """
        Retrieve all files belonging to a specific user.

        Args:
            db: SQLAlchemy Session object.
            user_id: ID of the user whose files to retrieve.

        Returns:
            List[File]: List of File model instances for the user.
        """
        files = db.query(File).filter(File.user_id == user_id).all()
        return files

    @classmethod
    def get_file(cls, db: Session, user_id: int, file_name: str) -> Optional[File]:
        """
        Retrieve a single file by user ID and file name.

        Args:
            db: SQLAlchemy Session object.
            user_id: ID of the user.
            file_name: Name of the file to retrieve.

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
        """
        Delete a file from the database.

        Args:
            db: SQLAlchemy Session object.
            user_id: ID of the user.
            file_name: Name of the file to delete.

        Raises:
            FileNotFoundError: If no file exists with the given name for the user.
        """
        db_file = cls.get_file(db=db, user_id=user_id, file_name=file_name)
        if db_file is None:
            raise FileNotFoundError(
                f"No file found with name '{file_name}' for user_id={user_id}"
            )
        db.delete(db_file)
        db.commit()
