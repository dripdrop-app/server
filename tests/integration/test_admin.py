from fastapi import status
from fastapi.testclient import TestClient


class AdminEndpoints:
    base_url = "/api/admin"
    cron = f"{base_url}/cron/run"


class TestRunCron:
    def test_run_cron_as_regular_user(self, client: TestClient, create_default_user):
        create_default_user()
        response = client.get(AdminEndpoints.cron)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_run_cron_as_admin_user(self, client: TestClient, create_default_user):
        create_default_user(admin=True)
        response = client.get(AdminEndpoints.cron)
        assert response.status_code == status.HTTP_200_OK
