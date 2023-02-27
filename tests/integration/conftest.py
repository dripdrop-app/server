import pytest
import shutil
from fastapi import status
from httpx import AsyncClient

from dripdrop.app import app
from dripdrop.apps.authentication.app import password_context
from dripdrop.apps.authentication.models import User
from dripdrop.database import database, AsyncSession
from dripdrop.dependencies import COOKIE_NAME
from dripdrop.models.base import Base
from dripdrop.services.s3 import s3
from dripdrop.settings import settings, ENV


@pytest.fixture(autouse=True)
async def check_environment():
    assert settings.env == ENV.TESTING


@pytest.fixture(autouse=True)
async def setup_database():
    async with database._engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.fixture(scope="session")
def delete_directories():
    def _delete_directories():
        try:
            shutil.rmtree("music_jobs")
        except Exception:
            pass
        try:
            shutil.rmtree("tags")
        except Exception:
            pass

    return _delete_directories


@pytest.fixture(scope="session")
async def http_client():
    async with AsyncClient() as client:
        yield client


@pytest.fixture(scope="session")
def clean_test_s3_folders():
    async def _clean_test_s3_folders():
        try:
            async for keys in s3.list_objects():
                for key in keys:
                    if key.startswith("test"):
                        continue
                    await s3.delete_file(filename=key)
        except Exception as e:
            print(e)
            pass

    return _clean_test_s3_folders


@pytest.fixture(scope="session")
async def client(clean_test_s3_folders, delete_directories):
    await clean_test_s3_folders()
    delete_directories()
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    await clean_test_s3_folders()
    delete_directories()


@pytest.fixture()
async def session():
    async with database.create_session() as session:
        yield session


@pytest.fixture
def create_user(session: AsyncSession):
    async def _create_user(email: str = ..., password: str = ..., admin=False):
        assert type(email) is str
        assert type(password) is str
        user = User(email=email, password=password_context.hash(password), admin=admin)
        session.add(user)
        await session.commit()
        return user

    return _create_user


@pytest.fixture
def create_and_login_user(client: AsyncClient, create_user):
    async def _create_and_login_user(
        email: str = ..., password: str = ..., admin=False
    ):
        user = await create_user(email=email, password=password, admin=admin)
        response = await client.post(
            "/api/auth/login", json={"email": email, "password": password}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.cookies.get(COOKIE_NAME, None) is not None
        return user

    return _create_and_login_user
