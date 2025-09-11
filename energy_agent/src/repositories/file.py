"""
...
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from core.exceptions.file import DuplicateFileNameError
from schemas.file import FileCreate
from models.file import File


class FileRepository:
    """
    ...
    """

    @classmethod
    def create_file(cls, db: Session, file_data: FileCreate) -> File:
        """
        ...
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
        ...
        """
        files = db.query(File).filter(File.user_id == user_id).all()
        return files

    @classmethod
    def get_file(cls, db: Session, user_id: int, file_name: str) -> Optional[File]:
        """
        ...
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
        ...
        """
        db_file = cls.get_file(db=db, user_id=user_id, file_name=file_name)
        if db_file is None:
            raise FileNotFoundError(
                f"No file found with name '{file_name}' for user_id={user_id}"
            )
        db.delete(db_file)
        db.commit()
