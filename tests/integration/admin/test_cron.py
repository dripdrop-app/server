from fastapi import status
from fastapi.testclient import TestClient

CRON_URL = "api/admin/cron/run"


def test_run_cron_when_not_logged_in(client: TestClient):
    response = client.get(CRON_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_run_cron_as_regular_user(client: TestClient, create_and_login_user):
    create_and_login_user(email="user@gmail.com", password="password")
    response = client.get(CRON_URL)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_run_cron_as_admin_user(client: TestClient, create_and_login_user):
    create_and_login_user(email="user@gmail.com", password="password", admin=True)
    response = client.get(CRON_URL)
    assert response.status_code == status.HTTP_200_OK
