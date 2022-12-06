from contextlib import asynccontextmanager
from dripdrop.settings import settings
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

database_url = URL.create(
    drivername="postgresql+asyncpg",
    username=settings.postgres_user,
    password=settings.postgres_password,
    host=settings.postgres_host,
    database=settings.postgres_database,
)

migration_database_url = database_url
migration_database_url.set(drivername="postgresql")


engine = create_async_engine(
    database_url,
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
