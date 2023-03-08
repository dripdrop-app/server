import pytest

from dripdrop.services import database
from dripdrop.models.base import Base
from dripdrop.settings import settings, ENV


@pytest.fixture(autouse=True)
async def check_environment():
    assert settings.env == ENV.TESTING


@pytest.fixture(autouse=True)
async def setup_database():
    database.engine.url = "sqlite+aiosqlite:///test.sqlite"
    async with database.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture()
async def session():
    async with database.create_session() as session:
        yield session
