"""
File cache manager for active user files.

This module provides a `FileCacheManager` class to manage caching of
active file data in Redis. It supports connecting to Redis, storing
and retrieving active file data for user sessions, and automatic key
expiration. The cache keys are namespaced per user and session.

It uses Redis as the backend and integrates with the application
settings for configuration.
"""

from uuid import UUID
from dataclasses import dataclass
from typing import Optional

from redis import Redis, RedisError

from core.config import settings


@dataclass
class FileCacheManager:
    """
    Manager for caching active file data in Redis.

    Attributes:
        host: Redis server host.
        port: Redis server port.
        db: Redis database index.
        client: Optional Redis client instance.
        default_ttl: Default time-to-live (in seconds) for cached entries.
    """

    host: str
    port: int
    db: int
    client: Optional[Redis] = None
    default_ttl: int = 3600

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
                decode_responses=True,
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
    def format_key(user_id: int, session_id: UUID) -> str:
        """
        Format the Redis key for a user's active file data.

        Args:
            user_id: ID of the user.
            session_id: ID of the session.

        Returns:
            str: Formatted Redis key.
        """
        return f"active_file:user{user_id}:session:{session_id}"

    def cache_active_file_data(
        self, user_id: int, session_id: UUID, file_data: dict
    ) -> None:
        """
        Cache active file data in Redis for a specific user session.

        Args:
            user_id: ID of the user.
            session_id: ID of the session.
            file_data: Dictionary containing file metadata to cache.
        """
        self._ensure_connected()
        key = self.format_key(user_id, session_id)
        try:
            self.client.hset(name=key, mapping=file_data)
            self.client.expire(key, self.default_ttl)
        except RedisError:
            ...

    def get_active_file_data(self, user_id: int, session_id: UUID) -> Optional[dict]:
        """
        Retrieve cached active file data for a user session.

        Args:
            user_id: ID of the user.
            session_id: ID of the session.

        Returns:
            Optional[dict]: Cached file data, or None if not found or on error.
        """
        self._ensure_connected()
        key = self.format_key(user_id, session_id)
        try:
            file_data = self.client.hgetall(key)
            if file_data:
                self.client.expire(key, self.default_ttl)
            return file_data
        except RedisError:
            ...


# Singleton instance of the file cache manager
file_cache = FileCacheManager(
    host=settings.redis.HOST,
    port=settings.redis.PORT,
    db=settings.redis.DB,
)
