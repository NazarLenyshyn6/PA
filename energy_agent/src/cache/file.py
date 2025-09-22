"""
File caching manager using Redis.

Handles storing, retrieving, and deleting user file metadata and content.
Uses pickle for serialization and applies TTL to cached entries.
"""

from dataclasses import dataclass
from typing import Optional, Dict
import pickle

from redis import Redis, RedisError

from core.config import settings
from schemas.file import FileData
from loaders.base import BaseLoader
from loaders.local import LocalLoader


@dataclass
class FileCacheManager:
    """Manages caching of user files in Redis."""

    host: str
    port: int
    db: int
    client: Optional[Redis] = None
    default_ttl: int = 3600
    loader: BaseLoader = LocalLoader

    def _ensure_connected(self):
        """
        Ensure that the Redis client is initialized.

        Raises:
            ConnectionError: If the Redis client has not been connected.
        """
        if self.client is None:
            raise ConnectionError(
                "Redis client is not initialized. Call 'connect_client()' first"
            )

    def connect_client(self) -> None:
        """
        Connect to the Redis server and initialize the client.
        """
        if self.client is None:
            self.client = Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=False,
                socket_keepalive=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )

    def close_client(self) -> None:
        """
        Close the Redis client connection and clean up resources.
        """
        if self.client:
            try:
                self.client.close()
            except RedisError:
                ...
            finally:
                self.client = None

    @staticmethod
    def format_key(user_id: int) -> str:
        """Format the Redis key for a user's cached files.

        Args:
            user_id (int): User identifier.

        Returns:
            str: Redis key string.
        """
        return f"files:user:{user_id}"

    def _update_cached_files(self, user_id: str, cached_files: Dict) -> None:
        """Serialize and update the user's cached files in Redis.

        Args:
            user_id (str): User identifier.
            cached_files (Dict): Dictionary of cached files.
        """
        key = self.format_key(user_id=user_id)
        try:
            self.client.set(key, pickle.dumps(cached_files))
            self.client.expire(key, self.default_ttl)

        except RedisError:
            ...

    def get_cached_files(self, user_id: int) -> Optional[Dict]:
        """Retrieve cached files for a user.

        Args:
            user_id (int): User identifier.

        Returns:
            Dict: Cached files mapping {file_name: FileData}, or empty dict if none.
        """
        self._ensure_connected()
        key = self.format_key(user_id=user_id)
        cached_files = self.client.get(key)
        return pickle.loads(cached_files) if cached_files else {}

    def add_file_to_cache(self, user_id: int, file_name: str, file_data: FileData):
        """Add or update a file in the user's cache.

        Loads file content using the loader and attaches it to FileData.

        Args:
            user_id (int): User identifier.
            file_name (str): Name of the file.
            file_data (FileData): File metadata to cache.
        """
        cached_files = self.get_cached_files(user_id=user_id)

        # Load file content from storage backend
        df = self.loader.load(file_data.storage_uri)
        file_data.df = df  # attach the loaded content to file metadata

        # Insert/update file entry in cache
        if cached_files:
            cached_files[file_name] = file_data
        else:
            cached_files = {file_name: file_data}

        # Push updated cache to Redis
        self._update_cached_files(user_id=user_id, cached_files=cached_files)

    def delete_file_from_cache(self, user_id: int, file_name: str):
        """Remove a specific file from the user's cache.

        Args:
            user_id (int): User identifier.
            file_name (str): Name of the file to remove.
        """
        # Get cached files
        cached_files = self.get_cached_files(user_id=user_id)
        if not cached_files:
            return

        # Remove file if exists in cache
        del cached_files[file_name]

        # Push updated cache to Redis
        self._update_cached_files(user_id=user_id, cached_files=cached_files)


# Singleton instance for global use
file_cache = FileCacheManager(
    host=settings.redis.HOST,
    port=settings.redis.PORT,
    db=settings.redis.DB,
)
