from typing import Any, Dict, Optional

import orjson
from redis.asyncio import Redis

from .base import BaseAsyncBackend


class RedisBackend(BaseAsyncBackend):
    """
    This class is used to connect and interact with Redis.

    Args:
        redis (:class:`redis.asyncio.Redis`): Redis client.
    """

    def __init__(self, redis: "Redis[Any]") -> None:
        self.redis = redis

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        data = await self.redis.get(key)
        if data:
            return orjson.loads(data)  # type: ignore
        return None

    async def set(
        self, key: str, value: Dict[str, Any], ex: Optional[int] = None
    ) -> Optional[bool]:
        data = orjson.dumps(value)
        return await self.redis.set(key, data, ex)

    async def update(self, key: str, value: Dict[str, Any]) -> Optional[bool]:
        data = orjson.dumps(value)
        return await self.redis.set(key, data, keepttl=True)

    async def delete(self, key: str) -> int:
        return await self.redis.delete(key)
