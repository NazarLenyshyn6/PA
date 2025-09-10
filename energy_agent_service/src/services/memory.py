"""
Service layer for agent memory management.

This module defines the `MemoryService` class, which provides high-level
operations for retrieving, creating, updating, caching, and deleting
agent memory. It integrates cache, database, and loader access into a
unified interface for efficient memory management.

Classes:
    MemoryService: Provides service-level memory operations backed by
        caching, persistence, and data loaders.

Instances:
    memory_service: Default instance of `MemoryService` configured with
        the global `memory_cache_manager` and `LocalLoader`.
"""

from typing import Optional, Type
from uuid import UUID
from dataclasses import dataclass
import pickle

from sqlalchemy.orm import Session

from loaders.base import BaseLoader
from loaders.local import LocalLoader
from repositories.memory import MemoryRepository
from cache.memory import MemoryCacheManager, memory_cache_manager
from schemas.memory import Memory


@dataclass
class MemoryService:
    """
    Service layer for managing agent memory.

    This class provides high-level APIs for working with memory records.
    It combines in-memory caching, database persistence, and data loaders
    into a single abstraction. Clients should use this service instead of
    directly calling repositories or cache managers.

    Attributes:
        _memory_cache_manager (MemoryCacheManager): Cache manager used
            to speed up memory retrieval and updates.
        loader (Type[BaseLoader]): Loader class used to fetch base data
            from local or remote storage.

    Methods:
        get_memory: Retrieve memory from cache, DB, or create if missing.
        create_memory: Initialize and persist a new memory record.
        update_memory_cache: Update memory fields in cache.
        save_memory: Persist cached memory back into the database.
        delete_memory: Remove a memory record from persistence.
    """

    _memory_cache_manager: MemoryCacheManager
    loader: Type[BaseLoader]

    def get_memory(
        self,
        db: Session,
        user_id: int,
        session_id: UUID,
        file_name: str,
        storage_uri: str,
    ) -> Memory:
        """
        Retrieve memory for a given user, session, and file.

        The service first attempts to fetch memory from cache. If absent,
        it falls back to the database. If no record exists, it creates a
        new memory record initialized with base data from the loader.

        Args:
            db: SQLAlchemy session.
            user_id: Identifier of the user.
            session_id: Unique identifier of the session.
            file_name: Associated file name.
            storage_uri: Path or URI to storage for initial data.

        Returns:
            Memory: The retrieved or newly created memory instance.
        """
        # Try retrieving memory from cache first for faster access
        cached_memory = self._memory_cache_manager.get_memory(
            session_id=session_id, file_name=file_name
        )
        if cached_memory is not None:
            return cached_memory

        # If cache miss, fetch memory from the database
        db_memory = MemoryRepository.get_memory(
            db=db, user_id=user_id, session_id=session_id, file_name=file_name
        )
        if db_memory is not None:
            memory_schema = Memory.model_validate(db_memory)

            # Cache the retrieved memory for future quick access
            self._memory_cache_manager.cache_memory(
                session_id=session_id, file_name=file_name, memory_schema=memory_schema
            )
            return memory_schema

        # If not found in cache or DB, create a new memory record
        return self.create_memory(
            db=db,
            user_id=user_id,
            session_id=session_id,
            storage_uri=storage_uri,
            file_name=file_name,
        )

    def create_memory(
        self,
        db: Session,
        user_id: int,
        session_id: UUID,
        file_name: str,
        storage_uri: str,
    ) -> Memory:
        """
        Create and persist a new memory record.

        Loads base data using the loader, initializes empty pickled
        contexts for summaries, code, user preferences, variables, and
        conversation, and persists the memory record into the database
        and cache.

        Args:
            db: SQLAlchemy session.
            user_id: Identifier of the user.
            session_id: Unique identifier of the session.
            file_name: Associated file name.
            storage_uri: Path or URI to storage.

        Returns:
            Memory: The newly created memory instance.
        """
        # Load the initial data from the loader (local or remote)
        df = self.loader.load(storage_uri=storage_uri)

        # Initialize a Memory schema with empty summaries and pickled variables
        memory_schema = Memory(
            user_id=user_id,
            session_id=session_id,
            file_name=file_name,
            messages=pickle.dumps([]),
            variables=pickle.dumps({"df": df}),
        )

        # Persist the memory record in the database
        MemoryRepository.create_memory(db=db, memory_schema=memory_schema)

        # Cache the memory record for fast future access
        self._memory_cache_manager.cache_memory(
            session_id=session_id, file_name=file_name, memory_schema=memory_schema
        )

        return memory_schema

    def update_memory_cache(
        self,
        db: Session,
        user_id: int,
        session_id: UUID,
        file_name: str,
        storage_uri: str,
        messages: Optional[bytes] = None,
        variables: Optional[bytes] = None,
    ):
        """
        Update cached memory fields.

        Retrieves the latest memory (creating it if necessary),
        applies updates to specified fields, and refreshes the cache.

        Args:
            db: SQLAlchemy session.
            user_id: Identifier of the user.
            session_id: Unique identifier of the session.
            file_name: Associated file name.
            storage_uri: Path or URI to storage.
            messages: .
            variables: Updated variable snapshot.
        """

        # Get current memory (create if missing)
        memory_history = self.get_memory(
            db=db,
            user_id=user_id,
            session_id=session_id,
            file_name=file_name,
            storage_uri=storage_uri,
        )

        # Update memory fields if provided
        if messages is not None:
            memory_history.messages = messages

        if variables is not None:
            memory_history.variables = variables

        # Refresh cache with updated memory
        self._memory_cache_manager.cache_memory(
            session_id=session_id, file_name=file_name, memory_schema=memory_history
        )

    def save_memory(
        self, db: Session, user_id: int, session_id: UUID, file_name: str
    ) -> None:
        """
        Persist cached memory into the database.

        Retrieves the memory from cache and updates the database record
        if present.

        Args:
            db: SQLAlchemy session.
            user_id: Identifier of the user.
            session_id: Unique identifier of the session.
            file_name: Associated file name.
        """

        cached_memory: Memory = self._memory_cache_manager.get_memory(
            session_id=session_id, file_name=file_name
        )

        if cached_memory is not None:
            MemoryRepository.update_memory(
                db=db,
                user_id=user_id,
                session_id=session_id,
                file_name=file_name,
                memory_schema=cached_memory,
            )

    def delete_memory(self, db: Session, user_id: int, file_name: str) -> None:
        """
        Delete a memory record.

        Args:
            db: SQLAlchemy session.
            user_id: Identifier of the user.
            file_name: Associated file name.
        """
        MemoryRepository.delete_memory(db=db, user_id=user_id, file_name=file_name)


# Default instance of the MemoryService for application usage
memory_service = MemoryService(memory_cache_manager, loader=LocalLoader)
