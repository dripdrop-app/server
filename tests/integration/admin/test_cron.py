from fastapi import status
from fastapi.testclient import TestClient

CRON_URL = "api/admin/cron/run"


def test_run_cron_as_regular_user(client: TestClient, create_and_login_user):
    create_and_login_user
    response = client.get(CRON_URL)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_run_cron_as_admin_user(
    client: TestClient, create_and_login_default_admin_user
):
    response = client.get(CRON_URL)
    assert response.status_code == status.HTTP_200_OK
