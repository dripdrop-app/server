from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from dripdrop.settings import settings


class Database:
    def __init__(self):
        self._engine = create_async_engine(
            settings.async_database_url, poolclass=NullPool, echo=False
        )
        self._session_maker = sessionmaker(
            bind=self._engine, expire_on_commit=False, class_=AsyncSession
        )

    @asynccontextmanager
    async def create_session(self):
        session: AsyncSession = self._session_maker()
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


database = Database()
