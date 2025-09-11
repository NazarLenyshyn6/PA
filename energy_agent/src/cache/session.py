"""
...
"""

from dataclasses import dataclass
from typing import Optional

from redis import Redis, RedisError

from core.config import settings


@dataclass
class SessionCacheManager:
    """
    ...
    """

    host: str
    port: int
    db: int
    key_prefix: str
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

    def cache_active_session_id(
        self,
        user_id: str,
        session_id: str,
    ) -> None:
        """
        ...
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
        ...
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
        ...
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
