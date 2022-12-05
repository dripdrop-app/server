from contextlib import asynccontextmanager
from dripdrop.settings import settings
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

MIGRATION_DATABASE_URL = settings.migration_database_url
DATABASE_URL = settings.database_url

engine = create_async_engine(
    DATABASE_URL,
    poolclass=NullPool,
    echo=False,
)
session_maker = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


@asynccontextmanager
async def create_session():
    db: AsyncSession = session_maker()
    try:
        yield db
    except Exception as e:
        await db.rollback()
        await db.close()
        raise e
    finally:
        await db.close()
