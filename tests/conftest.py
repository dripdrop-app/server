import pytest
from dripdrop.app import app
from dripdrop.authentication.models import Users
from dripdrop.database import session_maker
from dripdrop.dependencies import password_context
from dripdrop.models import OrmBase
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, insert
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool


test_engine = create_engine("sqlite:///test.sqlite", echo=False)
async_test_engine = create_async_engine(
    "sqlite+aiosqlite:///test.sqlite", poolclass=NullPool, echo=False
)


@pytest.fixture(autouse=True)
def setup_database():
    session_maker.configure(bind=async_test_engine)
    OrmBase.metadata.drop_all(bind=test_engine)
    OrmBase.metadata.create_all(bind=test_engine)
    yield


@pytest.fixture()
def client():
    client = TestClient(app)
    yield client


@pytest.fixture()
def create_user():
    def _create_user(email: str = ..., password: str = ..., admin=False):
        assert type(email) is str
        assert type(password) is str
        connection = test_engine.connect()
        connection.execute(
            insert(Users).values(
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

    return _create_and_login_user


TEST_EMAIL = "testuser@gmail.com"
TEST_PASSWORD = "testpassword"


class APIEndpoints:
    base_path = "/api"
