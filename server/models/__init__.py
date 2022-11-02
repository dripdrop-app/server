from contextlib import asynccontextmanager
from server.config import config
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession as DBSession,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

MIGRATION_DATABASE_URL = config.migration_database_url
DATABASE_URL = config.database_url
engine = create_async_engine(
    DATABASE_URL,
    poolclass=NullPool,
    echo=False,
)
session_maker = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=DBSession,
)


@asynccontextmanager
async def create_session():
    db: DBSession = session_maker()
    try:
        yield db
    except Exception as e:
        await db.rollback()
        await db.close()
        raise e
    finally:
        await db.close()
