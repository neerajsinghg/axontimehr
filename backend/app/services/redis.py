from app.core.config import settings
from app.core.logging import logger

try:
    import redis.asyncio as redis

    class RedisService:
        def __init__(self) -> None:
            self.redis_client: redis.Redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )

        async def ping(self) -> bool:
            try:
                return await self.redis_client.ping()
            except Exception as e:
                logger.error(f"Redis connection ping failed: {e}")
                return False

        async def close(self) -> None:
            try:
                await self.redis_client.close()
            except Exception:
                pass
except ImportError:
    class RedisService:
        async def ping(self) -> bool:
            return False

        async def close(self) -> None:
            pass

redis_service = RedisService()

