from contextlib import asynccontextmanager

from redis.asyncio.client import Redis

from dripdrop.settings import settings


@asynccontextmanager
async def create_client():
    client = Redis.from_url(settings.redis_url)
    try:
        yield client
    except Exception as e:
        raise e
    finally:
        await client.aclose()
        await client.connection_pool.disconnect()
