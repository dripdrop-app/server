from contextlib import asynccontextmanager
from enum import Enum
from sqlalchemy import Select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from typing import TypeVar, Tuple, overload, AsyncGenerator, Sequence, Literal

from dripdrop.settings import settings, ENV

T = TypeVar("T")


class StreamType(Enum):
    SCALARS = 0
    MAPPINGS = 1


engine = create_async_engine(
    settings.async_database_url,
    poolclass=NullPool,
    echo=settings.env == ENV.DEVELOPMENT,
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
) -> AsyncGenerator[Sequence[T], None]:
    ...


@overload
async def stream(
    query: Select[Tuple[T]],
    yield_per: int,
    session: AsyncSession,
    stream_type: Literal[StreamType.MAPPINGS],
) -> AsyncGenerator[Sequence[RowMapping], None]:
    ...


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
        elif stream_type == StreamType.MAPPINGS:
            rows = results.mappings().fetchmany(yield_per)
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


async def stream_mappings(
    query: Select[Tuple[T]], yield_per: int, session: AsyncSession
):
    async for rows in stream(
        query=query,
        yield_per=yield_per,
        session=session,
        stream_type=StreamType.MAPPINGS,
    ):
        yield rows
