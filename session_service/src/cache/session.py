"""
Redis-based session cache manager.

This module provides the `SessionCacheManager` class for managing active
user sessions in Redis. It supports caching, retrieving, and invalidating
session IDs for individual users, with automatic TTL management and
connection handling.

Components:
    - SessionCacheManager: Dataclass encapsulating Redis operations for session caching.
    - session_cache: Pre-configured global instance for active session management.
"""

from dataclasses import dataclass
from typing import Optional

from redis import Redis, RedisError

from core.config import settings


@dataclass
class SessionCacheManager:
    """
    Manager for caching active user session IDs in Redis.

    Attributes:
        host: Redis host address.
        port: Redis port number.
        db: Redis database index.
        key_prefix: Prefix for session keys in Redis.
        client: Redis client instance.
        default_ttl: Default time-to-live (TTL) for cached sessions in seconds.
    """

    host: str
    port: int
    db: int
    key_prefix: str
    client: Optional[Redis] = None
    default_ttl: int = 3600

    def _ensure_connected(self):
        """
        Ensure the Redis client is initialized.

        Raises:
            ConnectionError: If the Redis client is not connected.
        """
        if self.client is None:
            raise ConnectionError(
                "Redis client is not initialized. Call 'connect_client()' first"
            )

    def connect_client(self) -> None:
        """
        Initialize the Redis client if it has not been created yet.
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
        Close the Redis client connection and release resources.
        """
        if self.client:
            try:
                self.client.close()
            except RedisError:
                ...
            finally:
                self.client = None

    def cache_active_session_id(
        self,
        user_id: str,
        session_id: str,
    ) -> None:
        """
        Cache the active session ID for a specific user with TTL.

        Args:
            user_id: Unique user identifier.
            session_id: Session ID to cache.
        """
        self._ensure_connected()
        key = f"{self.key_prefix}{user_id}"
        try:
            self.client.set(name=key, value=session_id)
            self.client.expire(key, self.default_ttl)
        except RedisError:
            ...

    def get_active_session_id(self, user_id: str) -> Optional[str]:
        """
        Retrieve the cached active session ID for a specific user.

        Args:
            user_id: Unique user identifier.

        Returns:
            Optional[str]: The active session ID if it exists, otherwise None.
        """
        self._ensure_connected()
        key = f"{self.key_prefix}{user_id}"
        try:
            session_id = self.client.get(key)
            if session_id:
                self.client.expire(key, self.default_ttl)
            return session_id
        except RedisError:
            ...

    def deactivate_active_session_id(self, user_id: str) -> None:
        """
        Remove the active session ID for a specific user from the cache.

        Args:
            user_id (str): Unique user identifier.
        """
        self._ensure_connected()
        key = f"{self.key_prefix}{user_id}"
        try:
            self.client.delete(key)
        except RedisError:
            ...


# Global session cache manager instance
session_cache = SessionCacheManager(
    host=settings.redis.HOST,
    port=settings.redis.PORT,
    db=settings.redis.DB,
    key_prefix="session:active:user:",
)
