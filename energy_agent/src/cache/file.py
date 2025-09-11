"""
...
"""

from uuid import UUID
from dataclasses import dataclass
from typing import Optional

from redis import Redis, RedisError

from core.config import settings


@dataclass
class FileCacheManager:
    """
    ...
    """

    host: str
    port: int
    db: int
    client: Optional[Redis] = None
    default_ttl: int = 3600

    def _ensure_connected(self):
        """
        ...
        """
        if self.client is None:
            raise ConnectionError(
                "Redis client is not initialized. Call 'connect_client()' first"
            )

    def connect_client(self) -> None:
        """
        ...
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
        ...
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
        ...
        """
        return f"active_file:user{user_id}:session:{session_id}"

    def cache_active_file_data(
        self, user_id: int, session_id: UUID, file_data: dict
    ) -> None:
        """
        ...
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
        ...
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
