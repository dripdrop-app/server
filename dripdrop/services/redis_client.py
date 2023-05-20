from redis.asyncio.client import Redis
from contextlib import asynccontextmanager

from dripdrop.settings import settings


@asynccontextmanager
async def create_client():
    client = Redis.from_url(settings.redis_url)
    try:
        yield client
    except Exception as e:
        raise e
    finally:
        await client.close()
        await client.connection_pool.disconnect()
