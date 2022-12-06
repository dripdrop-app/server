import pytest
from dripdrop.app import app
from dripdrop.database import session_maker
from dripdrop.models import OrmBase
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool


test_engine = create_engine("sqlite:///./test.sqlite", echo=False)
async_test_engine = create_async_engine(
    "sqlite+aiosqlite:///./test.sqlite", poolclass=NullPool, echo=False
)


@pytest.fixture(autouse=True)
def setup():
    session_maker.configure(bind=async_test_engine)
    OrmBase.metadata.drop_all(bind=test_engine)
    OrmBase.metadata.create_all(bind=test_engine)
    yield
    OrmBase.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def client():
    client = TestClient(app)
    yield client


@pytest.fixture()
def create_user(client: TestClient):
    def _create_user(email: str = ..., password: str = ..., admin=False):
        assert type(email) is str
        assert type(password) is str
        response = client.post(
            "/api/auth/create",
            json={"email": email, "password": password},
        )
        assert response.status_code == 200
        if admin:
            test_engine.execute(
                f"update users set admin = 'true' where email = '{email}'"
            )

    return _create_user
