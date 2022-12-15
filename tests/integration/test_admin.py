import pytest
from ..conftest import APIEndpoints, TEST_EMAIL, TEST_PASSWORD
from fastapi import status
from fastapi.testclient import TestClient
from dripdrop.services.cron import cron_service


class AdminEndpoints:
    base_url = f"{APIEndpoints.base_path}/admin"
    cron = f"{base_url}/cron/run"


def test_run_cron_as_regular_user(client: TestClient, create_user):
    create_user(email=TEST_EMAIL, password=TEST_PASSWORD)
    response = client.get(AdminEndpoints.cron)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_run_cron_as_admin_user(
    monkeypatch: pytest.MonkeyPatch, client: TestClient, create_user
):
    create_user(email=TEST_EMAIL, password=TEST_PASSWORD, admin=True)
    monkeypatch.setattr(cron_service, "run_cron_jobs", lambda: None)
    response = client.get(AdminEndpoints.cron)
    assert response.status_code == status.HTTP_200_OK
