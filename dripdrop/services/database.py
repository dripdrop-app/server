from contextlib import asynccontextmanager
from enum import Enum
from typing import AsyncGenerator, Literal, Sequence, Tuple, TypeVar, overload

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from dripdrop.settings import settings

T = TypeVar("T")


class StreamType(Enum):
    SCALARS = 0


engine = create_async_engine(
    settings.async_database_url,
    poolclass=NullPool,
    echo=False,
)
session_maker = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


@asynccontextmanager
async def create_session():
    session: AsyncSession = session_maker()
    try:
        yield session
    except Exception as e:
        await session.rollback()
        raise e
    finally:
        await session.close()


@overload
async def stream(
    query: Select[Tuple[T]],
    yield_per: int,
    session: AsyncSession,
    stream_type: Literal[StreamType.SCALARS],
) -> AsyncGenerator[Sequence[T], None]: ...


async def stream(
    query: Select[Tuple[T]],
    yield_per: int,
    session: AsyncSession,
    stream_type: StreamType,
):
    page = 0
    while True:
        results = await session.execute(query.offset(page * yield_per))
        if stream_type == StreamType.SCALARS:
            rows = results.scalars().fetchmany(yield_per)
        if not rows:
            break
        yield rows
        page += 1


async def stream_scalars(
    query: Select[Tuple[T]], yield_per: int, session: AsyncSession
):
    async for rows in stream(
        query=query,
        yield_per=yield_per,
        session=session,
        stream_type=StreamType.SCALARS,
    ):
        yield rows


async def stream_scalar(query: Select[Tuple[T]], session: AsyncSession):
    async for rows in stream(
        query=query,
        yield_per=1,
        session=session,
        stream_type=StreamType.SCALARS,
    ):
        yield rows[0]
