from typing import Annotated

from fastapi import Depends

from dripdrop.services import database, redis_client
from dripdrop.services.database import AsyncSession
from dripdrop.services.redis_client import Redis


async def create_database_session():
    async with database.create_session() as session:
        yield session


async def create_redis_client():
    async with redis_client.create_client() as client:
        yield client


DatabaseSession = Annotated[AsyncSession, Depends(create_database_session)]

RedisClient = Annotated[Redis, Depends(create_redis_client)]
