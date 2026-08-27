import asyncio
import logging
from typing import Optional

import redis.asyncio as redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


class RedisClient:
    def __init__(self, url: str):
        self._url = url
        self._client: Optional[redis.Redis] = None
        self._lock = asyncio.Lock()

    async def connect(self) -> None:
        client = redis.from_url(
            self._url,
            encoding="utf-8",
            decode_responses=True,
            retry_on_timeout=True,
            health_check_interval=30,
            socket_connect_timeout=5,
            socket_timeout=5,
            max_connections=20,
        )
        try:
            await client.ping()
        except RedisError:
            logger.exception("Failed to connect to Redis")
            raise
        self._client = client
        logger.info("Connected to Redis successfully.")

    async def disconnect(self) -> None:
        if self._client:
            await self._client.close()
            self._client = None
            logger.info("Disconnected from Redis.")

    async def get_client(self) -> redis.Redis:
        if self._client is None:
            async with self._lock:
                if self._client is None:
                    await self.connect()
        return self._client


def build_redis_client() -> RedisClient:
    import os
    url = os.getenv("REDIS_URL", "redis://localhost:6379")
    return RedisClient(url)


redis_manager = build_redis_client()