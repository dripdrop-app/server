from contextlib import asynccontextmanager, contextmanager
from dripdrop.settings import settings
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool


class Database:
    def __init__(self):
        self.async_engine = create_async_engine(
            settings.async_database_url, poolclass=NullPool, echo=False
        )
        self.async_session_maker = sessionmaker(
            bind=self.async_engine, expire_on_commit=False, class_=AsyncSession
        )
        self.engine = create_engine(
            settings.database_url, poolclass=NullPool, echo=False
        )
        self.session_maker = sessionmaker(bind=self.engine, expire_on_commit=False)

    @asynccontextmanager
    async def async_create_session(self):
        session: AsyncSession = self.async_session_maker()
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

    @contextmanager
    def create_session(self):
        session: Session = self.session_maker()
        try:
            yield session
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()


database = Database()
