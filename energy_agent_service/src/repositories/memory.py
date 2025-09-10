"""
Database repository for memory persistence.

This module defines the `MemoryRepository` class, which provides CRUD
(Create, Read, Update, Delete) operations for agent memory records stored
in the database. It acts as an abstraction over SQLAlchemy queries and
encapsulates all low-level persistence logic.

Classes:
    MemoryRepository: Repository for creating, retrieving, updating,
        and deleting agent memory records.
"""

from uuid import UUID
from typing import Optional

from sqlalchemy.orm import Session

from schemas.memory import Memory as MemorySchema
from models.memory import Memory as MemoryModel


class MemoryRepository:
    """
    Repository for managing memory records.

    Provides class methods to create, retrieve, update, and delete memory
    records in the database. Each method accepts a SQLAlchemy session and
    interacts with the `MemoryModel` ORM class. Designed for use within
    higher-level services and application workflows.

    Methods:
        create_memory: Create and persist a new memory record.
        get_memory: Retrieve a memory record by identifiers.
        update_memory: Update fields of an existing memory record.
        delete_memory: Remove a memory record by user and file name.
    """

    @classmethod
    def create_memory(cls, db: Session, memory_schema: MemorySchema) -> MemoryModel:
        """
        Create and persist a new memory record.

        Args:
            db: SQLAlchemy database session.
            memory_schema: Pydantic schema containing
                memory details to be stored.

        Returns:
            MemoryModel: The newly created memory record.
        """
        db_memory = MemoryModel(**memory_schema.model_dump())
        db.add(db_memory)
        db.commit()
        db.refresh(db_memory)
        return db_memory

    @classmethod
    def get_memory(
        cls, db: Session, user_id: int, session_id: UUID, file_name: str
    ) -> Optional[MemoryModel]:
        """
        Retrieve a memory record by identifiers.

        Args:
            db: SQLAlchemy database session.
            user_id: Identifier of the user.
            session_id: Unique identifier of the session.
            file_name: Name of the file associated with the memory.

        Returns:
            Optional[MemoryModel]: The memory record if found, otherwise None.
        """
        return (
            db.query(MemoryModel)
            .filter_by(user_id=user_id, session_id=session_id, file_name=file_name)
            .first()
        )

    @classmethod
    def update_memory(
        cls,
        db: Session,
        user_id: int,
        session_id: UUID,
        file_name: str,
        memory_schema: MemorySchema,
    ) -> None:
        """
        Update an existing memory record.

        Args:
            db: SQLAlchemy database session.
            user_id: Identifier of the user.
            session_id: Unique identifier of the session.
            file_name: Name of the file associated with the memory.
            memory_schema: Schema containing updated values.

        Notes:
            Only non-null fields in `memory_schema` overwrite existing values.
        """
        memory_history = cls.get_memory(
            db=db, user_id=user_id, session_id=session_id, file_name=file_name
        )

        if memory_schema.messages is not None:
            memory_history.messages = memory_schema.messages

        if memory_schema.variables is not None:
            memory_history.variables = memory_schema.variables

        db.commit()

    @classmethod
    def delete_memory(cls, db: Session, user_id: int, file_name: str) -> None:
        """
        Delete a memory record.

        Args:
            db: SQLAlchemy database session.
            user_id: Identifier of the user.
            file_name: Name of the file associated with the memory.

        Returns:
            None
        """
        db.query(MemoryModel).filter(
            MemoryModel.user_id == user_id, MemoryModel.file_name == file_name
        ).delete(synchronize_session=False)

        db.commit()
