"""
Agent memory cache manager.

This module provides a Redis-backed cache manager for storing and retrieving
agent memory objects. The cache enables fast access to serialized agent
memory data, reducing load on persistent storage. Memory objects are stored
with an expiration (TTL) to ensure data freshness and to prevent unbounded
cache growth.

Classes:
    MemoryCacheManager: Manager class for connecting to Redis,
        formatting cache keys, and handling serialization of agent memory
        objects.
"""

from uuid import UUID
from dataclasses import dataclass
from typing import Optional
import pickle

from redis import Redis, RedisError

from core.config import settings
from schemas.memory import Memory


@dataclass
class MemoryCacheManager:
    """
    Redis-backed cache manager for agent memory.

    This class manages serialization, caching, and retrieval of agent memory
    objects in Redis. It provides connection lifecycle handling, key
    formatting, and automatic TTL (time-to-live) management.

    Attributes:
        host: Redis server host address.
        port: Redis server port number.
        db: Redis database index to use.
        client: Active Redis client instance. Defaults to None.
        default_ttl: Default cache expiration time in seconds. Defaults to 3600 (1 hour).
    """

    host: str
    port: int
    db: int
    client: Optional[Redis] = None
    default_ttl: int = 3600

    def _ensure_connected(self):
        """
        Ensure that the Redis client is connected.

        Raises:
            ConnectionError: If the client has not been initialized.
        """
        if self.client is None:
            raise ConnectionError(
                "Redis client is not initialized. Call 'connect_client()' first"
            )

    def connect_client(self) -> None:
        """
        Establish a connection to the Redis server.

        Creates a Redis client if one is not already connected.
        Configures socket options to handle keepalive and connection timeouts.
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
        Close the Redis client connection.

        Ensures that the client is safely closed and set to None.
        Any Redis-related errors during closure are silently ignored.
        """
        if self.client:
            try:
                self.client.close()
            except RedisError:
                ...
            finally:
                self.client = None

    @staticmethod
    def format_key(session_id: UUID, file_name: str) -> str:
        """
        Format a Redis key for agent memory.

        Args:
            session_id (UUID): Unique session identifier.
            file_name (str): Name of the file or context tied to the memory.

        Returns:
            str: Redis cache key in the format
                 'energy_agent_memory:session:<session_id>:file:<file_name>'.
        """
        return f"energy_agent_memory:session:{session_id}:file:{file_name}"

    def get_memory(self, session_id: UUID, file_name: str) -> Optional[Memory]:
        """
        Retrieve an agent memory object from Redis.

        Args:
            session_id: Unique session identifier.
            file_name: Name of the file or context tied to the memory.

        Returns:
            Optional[Memory]: Deserialized Memory object if found,
            otherwise None.

        Notes:
            - Resets the TTL of the key upon successful retrieval.
        """
        self._ensure_connected()
        key = self.format_key(session_id, file_name)
        try:
            memory_bytes = self.client.get(key)
            if memory_bytes:
                self.client.expire(key, self.default_ttl)
                return pickle.loads(memory_bytes)
            return memory_bytes
        except RedisError:
            ...

    def cache_memory(self, session_id: UUID, file_name: str, memory_schema: Memory):
        """
        Cache an agent memory object in Redis.

        Args:
            session_id: Unique session identifier.
            file_name: Name of the file or context tied to the memory.
            memory_schema: Memory object to serialize and cache.

        Notes:
            - Stores the memory object as a pickled binary payload.
            - Applies the default TTL to automatically expire old entries.
        """
        self._ensure_connected()
        key = self.format_key(session_id, file_name)
        try:
            memory_bytes = pickle.dumps(memory_schema)
            self.client.set(key, memory_bytes)
            self.client.expire(key, self.default_ttl)
        except RedisError:
            ...


# Configured cache manager for agent memory across the app.
memory_cache_manager = MemoryCacheManager(
    host=settings.redis.HOST,
    port=settings.redis.PORT,
    db=settings.redis.DB,
)
