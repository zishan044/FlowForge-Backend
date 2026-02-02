import json
from typing import Any
from redis.asyncio import Redis
from app.core.config import settings

redis: Redis | None = None

async def init_redis():
    global redis
    redis = Redis.from_url(
        url=settings.REDIS_URL,
        decode_responses=True
    )

async def close_redis():
    if redis:
        await redis.close()


async def get_cache(key: str):
    if not redis:
        return None
    return await redis.get(key)


async def set_cache(key: str, value: Any, ttl: int = settings.REDIS_DEFAULT_TTL):
    if not redis:
        return
    await redis.set(key, json.dumps(value), ex=ttl)


async def delete_cache(key: str):
    if redis:
        await redis.delete(key)

