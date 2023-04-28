from fastapi import Depends
from typing import Annotated

from dripdrop.services import database
from dripdrop.services.database import AsyncSession


async def create_database_session():
    async with database.create_session() as session:
        yield session


DatabaseSession = Annotated[AsyncSession, Depends(create_database_session)]
