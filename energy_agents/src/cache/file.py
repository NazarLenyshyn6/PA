"""..."""

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
    """
    Manages caching of user files in Redis.

    - Connects to Redis and maintains a client session.
    - Stores, retrieves, and deletes cached file metadata and data.
    - Uses pickle for serialization/deserialization of Python objects.
    - Applies TTL (time-to-live) to auto-expire cached entries.
    """

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
        """
        Format the key for storing/retrieving user files.

        Args:
            user_id (int): ID of the user.

        Returns:
            str: Redis key.
        """
        return f"files:user:{user_id}"

    def _update_cached_files(self, user_id: str, cached_files: Dict) -> None:
        key = self.format_key(user_id=user_id)
        try:
            # Serialize the cache dictionary and store in Redis
            self.client.set(key, pickle.dumps(cached_files))

            # Reset TTL so the cache auto-expires
            self.client.expire(key, self.default_ttl)

        except RedisError:
            ...

    def get_cached_files(self, user_id: int) -> Optional[Dict]:
        """
        Retrieve cached files for a given user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            dict: Cached files {file_name: FileData} or empty dict if none."""
        self._ensure_connected()
        # Fetch raw serialized data
        key = self.format_key(user_id=user_id)
        cached_files = self.client.get(key)

        # Deserialize pickle into Python dict or return empty dict
        return pickle.loads(cached_files) if cached_files else {}

    def add_file_to_cache(self, user_id: int, file_name: str, file_data: FileData):
        """
        Add a file to the user's cache.

        Steps:
        1. Retrieve existing cached files.
        2. Load file content (e.g., DataFrame) using loader.
        3. Attach loaded content to `FileData`.
        4. Add/update the file in the cache dictionary.
        5. Save back to Redis with TTL.
        """
        # Get existing cached files for this user
        cached_files = self.get_cached_files(user_id=user_id)

        # Load file contents from storage
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
        """
        Delete a specific file from the user's cache.

        Steps:
        1. Retrieve cached files.
        2. Remove the given file if it exists.
        3. Save the updated cache back to Redis.
        """
        # Get cached files
        cached_files = self.get_cached_files(user_id=user_id)
        if not cached_files:
            return

        # Remove file if exists in cache
        del cached_files[file_name]

        # Push updated cache to Redis
        self._update_cached_files(user_id=user_id, cached_files=cached_files)


# Singleton instance of the file cache manager
file_cache = FileCacheManager(
    host=settings.redis.HOST,
    port=settings.redis.PORT,
    db=settings.redis.DB,
)
