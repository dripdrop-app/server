import asyncio
import os
import pytest
import subprocess
import time
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, insert
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from dripdrop.app import app
from dripdrop.authentication.app import password_context
from dripdrop.authentication.models import User
from dripdrop.dependencies import COOKIE_NAME
from dripdrop.models.database import database
from dripdrop.models.base import Base
from dripdrop.settings import settings


test_engine = create_engine(
    settings.test_database_url,
    echo=False,
    connect_args={"check_same_thread": False},
)
async_test_engine = create_async_engine(
    settings.test_async_database_url, poolclass=NullPool, echo=False
)

# Fix found here https://github.com/pytest-dev/pytest-asyncio/issues/207
# Need to create a single event loop that all instances will use


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def client(event_loop):
    with TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True)
def setup_database():
    database.async_session_maker.configure(bind=async_test_engine)
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield


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
def create_default_user(create_and_login_user):
    create_and_login_user(email=TEST_EMAIL, password=TEST_PASSWORD, admin=False)


@pytest.fixture()
def run_worker():
    process = subprocess.Popen(
        ["python", "worker.py"],
        env={
            **os.environ,
            "ASYNC_DATABASE_URL": settings.test_async_database_url,
            "DATABASE_URL": settings.test_database_url,
        },
    )
    yield
    process.kill()
    while process.poll() is None:
        time.sleep(1)


TEST_EMAIL = "testuser@gmail.com"
TEST_PASSWORD = "testpassword"


class APIEndpoints:
    base_path = "/api"
