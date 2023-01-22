import os
import pytest
import subprocess
import time
from datetime import datetime
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
def session():
    with database.create_session() as session:
        yield session


# Fix found here https://github.com/pytest-dev/pytest-asyncio/issues/207
# Need to create a single event loop that all instances will use


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as client:
        yield client


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


@pytest.fixture
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


@pytest.fixture
def run_worker(clean_test_s3_folders):
    clean_test_s3_folders()
    process = subprocess.Popen(
        ["python", "worker.py"],
        env={
            **os.environ,
            "ASYNC_DATABASE_URL": settings.test_async_database_url,
            "DATABASE_URL": settings.test_database_url,
        },
    )
    yield process
    process.kill()
    while process.poll() is None:
        time.sleep(1)
    clean_test_s3_folders()
