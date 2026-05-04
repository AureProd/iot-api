import logging

import redis.asyncio as redis
from iot_api.core import config

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self._client = None

    async def connect(self):
        """Initialise le pool de connexions de manière asynchrone."""
        if self._client: return
        
        self._client = redis.from_url(
            config.REDIS_URL, 
            decode_responses=True,
            socket_timeout=5
        )
        
        await self._client.ping() # Check connection
        logger.info("Redis connected")

    async def close(self):
        """Ferme proprement le pool."""
        if not self._client: return
        
        await self._client.close()
        self._client = None
        logger.info("Redis disconnected")

    async def set(self, key: str, value: str, ttl: int = 600):
        await self._client.setex(key, ttl, value)

    async def get(self, key: str) -> str | None:
        return await self._client.get(key)
    
    async def pop(self, key: str) -> str | None:
        pipe = self._client.pipeline()
        pipe.get(key)
        pipe.delete(key)
        results = await pipe.execute() 
        return results[0]
