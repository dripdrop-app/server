import pytest
import time
from datetime import datetime
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import insert
from sqlalchemy.engine import Connection

from dripdrop.app import app
from dripdrop.apps.authentication.app import password_context
from dripdrop.apps.authentication.models import User
from dripdrop.database import database
from dripdrop.dependencies import COOKIE_NAME
from dripdrop.models.base import Base
from dripdrop.settings import settings


@pytest.fixture(autouse=True)
def check_environment():
    assert settings.env == "testing"


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=database.engine)
    Base.metadata.create_all(bind=database.engine)
    yield


@pytest.fixture
def db():
    return database.engine.connect()


# Fix found here https://github.com/pytest-dev/pytest-asyncio/issues/207
# Need to create a single event loop that all instances will use


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def test_email():
    return "testuser@gmail.com"


@pytest.fixture
def test_password():
    return "testpassword"


@pytest.fixture
def function_timeout():
    def _function_timeout(timeout: int = ..., function=...):
        start_time = datetime.now()
        while True:
            result = function()
            if result is not None:
                return result
            current_time = datetime.now()
            duration = current_time - start_time
            assert duration.seconds < timeout
            time.sleep(1)

    return _function_timeout


@pytest.fixture
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


@pytest.fixture
def create_and_login_user(client: TestClient, create_user):
    def _create_and_login_user(email: str = ..., password: str = ..., admin=False):
        create_user(email, password, admin)
        response = client.post(
            "/api/auth/login", json={"email": email, "password": password}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.cookies.get(COOKIE_NAME, None) is not None

    return _create_and_login_user


@pytest.fixture
def create_and_login_default_user(create_and_login_user, test_email, test_password):
    create_and_login_user(email=test_email, password=test_password, admin=True)
