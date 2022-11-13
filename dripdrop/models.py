from contextlib import asynccontextmanager
from datetime import datetime
from dripdrop.settings import settings
from pydantic import BaseModel, SecretStr
from sqlalchemy import Column, String, Boolean, text, TIMESTAMP, MetaData
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
)
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
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


metadata = MetaData()
OrmBase = declarative_base(metadata=metadata)


class Users(OrmBase):
    __tablename__ = "users"
    email = Column(String, primary_key=True)
    password = Column(String, nullable=False)
    admin = Column(Boolean, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )
    google_account = relationship(
        "GoogleAccounts",
        back_populates="user",
        uselist=False,
    )
    music_jobs = relationship("MusicJobs", back_populates="user")


class ApiBase(BaseModel):
    class Config:
        orm_mode = True


class User(ApiBase):
    email: str
    password: SecretStr
    admin: bool
    created_at: datetime
