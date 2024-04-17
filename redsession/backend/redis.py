from __future__ import annotations

from typing import TYPE_CHECKING, Any

try:
    import orjson as json
except ImportError:
    import json  # type: ignore

if TYPE_CHECKING:
    from redis.asyncio import Redis

from .base import BaseAsyncBackend


class RedisBackend(BaseAsyncBackend):
    """
    This class is used to connect and interact with Redis.

    Args:
        redis (:obj:`redis.asyncio.Redis`): Async Redis client.
    """

    def __init__(self, redis: Redis[Any]) -> None:  # type: ignore
        self.redis = redis

    async def get(self, key: str) -> dict[str, Any] | None:
        data = await self.redis.get(key)
        if data:
            return json.loads(data)  # type: ignore
        return None

    async def set(self, key: str, value: dict[str, Any], ex: int | None = None) -> Any:
        data = json.dumps(value)
        return await self.redis.set(key, data, ex)

    async def update(self, key: str, value: dict[str, Any]) -> Any:
        data = json.dumps(value)
        return await self.redis.set(key, data, keepttl=True)

    async def delete(self, key: str) -> Any:
        return await self.redis.delete(key)
