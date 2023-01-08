import pytest
import time
from datetime import datetime, timezone
from fastapi import status
from fastapi.testclient import TestClient

JOBS_URL = "/api/music/jobs"


@pytest.mark.noauth
def test_get_jobs_when_not_logged_in(client: TestClient):
    response = client.get(f"{JOBS_URL}/1/10")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_jobs_with_no_results(client: TestClient):
    response = client.get(f"{JOBS_URL}/1/10")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_jobs_with_out_of_range_page(
    client: TestClient, create_music_job, test_music_job
):
    for i in range(15):
        create_music_job(**{**test_music_job, "id": f"test_{i}"})
    response = client.get(f"{JOBS_URL}/3/10")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_jobs_with_single_result(
    client: TestClient, create_music_job, test_music_job, assert_jobs_response
):
    create_music_job(**test_music_job)
    response = client.get(f"{JOBS_URL}/1/10")
    assert response.status_code == status.HTTP_200_OK
    assert_jobs_response(json=response.json(), jobs_length=1, total_pages=1)


def test_get_jobs_with_partial_page(
    client: TestClient, create_music_job, test_music_job, assert_jobs_response
):
    for i in range(15):
        create_music_job(**{**test_music_job, "id": f"test_{i}"})
    response = client.get(f"{JOBS_URL}/1/20")
    assert response.status_code == status.HTTP_200_OK
    assert_jobs_response(json=response.json(), jobs_length=15, total_pages=1)


def test_get_jobs_with_multiple_pages(
    client: TestClient, create_music_job, test_music_job, assert_jobs_response
):
    for i in range(20):
        create_music_job(**{**test_music_job, "id": f"test_{i}"})
    response = client.get(f"{JOBS_URL}/1/10")
    assert response.status_code == status.HTTP_200_OK
    assert_jobs_response(json=response.json(), jobs_length=10, total_pages=2)


def test_get_jobs_with_deleted_jobs(
    client: TestClient, create_music_job, test_music_job, assert_jobs_response
):
    for i in range(10):
        create_music_job(
            **{
                **test_music_job,
                "id": f"test_{i}",
                "deleted_at": datetime.now(timezone.utc) if i % 2 == 0 else None,
            }
        )
    response = client.get(f"{JOBS_URL}/1/5")
    assert response.status_code == status.HTTP_200_OK
    assert_jobs_response(json=response.json(), jobs_length=5, total_pages=1)


def test_get_jobs_are_in_descending_order(
    client: TestClient, create_music_job, test_music_job, assert_jobs_response
):
    for i in range(5):
        create_music_job(**{**test_music_job, "id": f"test_{i}"})
        time.sleep(1)
    response = client.get(f"{JOBS_URL}/1/5")
    assert response.status_code == status.HTTP_200_OK
    assert_jobs_response(json=response.json(), jobs_length=5, total_pages=1)
    jobs = response.json()["jobs"]
    for i in range(1, len(jobs)):
        assert jobs[i]["createdAt"] < jobs[i - 1]["createdAt"]
