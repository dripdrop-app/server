import multiprocessing
import pytest
from dripdrop.app import app
from dripdrop.authentication.models import User
from dripdrop.models.database import db as Db
from dripdrop.models.register import metadata
from dripdrop.dependencies import password_context, COOKIE_NAME
from dripdrop.settings import settings
from fastapi import status
from fastapi.testclient import TestClient
from redis import Redis
from sqlalchemy import create_engine, insert
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool
from worker import run_worker as _run_worker


test_engine = create_engine(
    "sqlite:///test.sqlite", echo=False, connect_args={"check_same_thread": False}
)
async_test_engine = create_async_engine(
    "sqlite+aiosqlite:///test.sqlite", poolclass=NullPool, echo=False
)


@pytest.fixture(autouse=True)
def setup_database():
    Db.async_session_maker.configure(bind=async_test_engine)
    metadata.drop_all(bind=test_engine)
    metadata.create_all(bind=test_engine)
    yield


@pytest.fixture()
def client():
    client = TestClient(app)
    yield client


@pytest.fixture()
def db():
    return test_engine.connect()


@pytest.fixture()
def create_user(db: Connection):
    def _create_user(email: str = ..., password: str = ..., admin=False):
        assert type(email) is str
        assert type(password) is str
        db.execute(
            insert(User).values(
                email=email, password=password_context.hash(password), admin=admin
            )
        )

    return _create_user


@pytest.fixture()
def create_and_login_user(client: TestClient, create_user):
    def _create_and_login_user(email: str = ..., password: str = ..., admin=False):
        create_user(email, password, admin)
        response = client.post(
            "/api/auth/login", json={"email": email, "password": password}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.cookies.get(COOKIE_NAME, None) is not None

    return _create_and_login_user


@pytest.fixture()
def run_worker():
    connection = Redis.from_url(settings.redis_url)
    connection.flushall()
    connection.close()
    process = multiprocessing.Process(None, target=_run_worker)
    process.start()
    yield
    process.terminate()


TEST_EMAIL = "testuser@gmail.com"
TEST_PASSWORD = "testpassword"


class APIEndpoints:
    base_path = "/api"
