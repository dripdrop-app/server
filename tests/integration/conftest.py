# import os
import pytest

# import subprocess
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from dripdrop.app import app
from dripdrop.apps.authentication.app import password_context
from dripdrop.apps.authentication.models import User
from dripdrop.database import database
from dripdrop.dependencies import COOKIE_NAME
from dripdrop.models.base import Base
from dripdrop.services.boto3 import boto3_service
from dripdrop.settings import settings, ENV


@pytest.fixture(autouse=True)
def check_environment():
    assert settings.env == ENV.TESTING


@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=database.engine)
    Base.metadata.create_all(bind=database.engine)
    yield


@pytest.fixture
def session():
    with database.create_session() as session:
        yield session


@pytest.fixture(scope="session")
def clean_test_s3_folders():
    def _clean_test_s3_folders():
        try:
            for keys in boto3_service.list_objects():
                for key in keys:
                    if key.startswith("test"):
                        continue
                    boto3_service.delete_file(filename=key)
        except Exception as e:
            print(e)
            pass

    return _clean_test_s3_folders


# Fix found here https://github.com/pytest-dev/pytest-asyncio/issues/207
# Need to create a single event loop that all instances will use


@pytest.fixture(scope="session")
def client(clean_test_s3_folders):
    clean_test_s3_folders()
    with TestClient(app) as client:
        yield client
    clean_test_s3_folders()


@pytest.fixture
def create_user(session: Session):
    def _create_user(email: str = ..., password: str = ..., admin=False):
        assert type(email) is str
        assert type(password) is str
        user = User(email=email, password=password_context.hash(password), admin=admin)
        session.add(user)
        session.commit()
        return user

    return _create_user


@pytest.fixture
def create_and_login_user(client: TestClient, create_user):
    def _create_and_login_user(email: str = ..., password: str = ..., admin=False):
        user = create_user(email=email, password=password, admin=admin)
        response = client.post(
            "/api/auth/login", json={"email": email, "password": password}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.cookies.get(COOKIE_NAME, None) is not None
        return user

    return _create_and_login_user
