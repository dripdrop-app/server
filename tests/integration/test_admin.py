from fastapi import status
from fastapi.testclient import TestClient

from .conftest import TEST_EMAIL, TEST_PASSWORD


class AdminEndpoints:
    base_url = "/api/admin"
    cron = f"{base_url}/cron/run"


class TestRunCron:
    def test_run_cron_as_regular_user(self, client: TestClient, create_and_login_user):
        create_and_login_user(email=TEST_EMAIL, password=TEST_PASSWORD)
        response = client.get(AdminEndpoints.cron)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_run_cron_as_admin_user(self, client: TestClient, create_and_login_user):
        create_and_login_user(email=TEST_EMAIL, password=TEST_PASSWORD, admin=True)
        response = client.get(AdminEndpoints.cron)
        assert response.status_code == status.HTTP_200_OK
