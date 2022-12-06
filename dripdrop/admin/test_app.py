import pytest
from dripdrop.conftest import TestClient
from dripdrop.services.cron import cron_service


def test_run_cron_as_regular_user(client: TestClient, create_user):
    create_user(email="testadmin@gmail.com", password="testpassword")
    response = client.get("/api/admin/cron/run")
    assert response.status_code == 403


def test_run_cron_as_admin_user(
    monkeypatch: pytest.MonkeyPatch, client: TestClient, create_user
):
    create_user(email="testadmin@gmail.com", password="testpassword", admin=True)
    monkeypatch.setattr(cron_service, "run_cron_jobs", lambda: None)
    response = client.get("/api/admin/cron/run")
    assert response.status_code == 200
