import pytest
from fastapi import status
from fastapi.testclient import TestClient

CREATE_URL = "/api/music/jobs/create"


@pytest.mark.noauth
def test_creating_job_when_not_logged_in(
    client: TestClient,
    test_file_params,
    test_youtube_url,
):
    response = client.post(
        CREATE_URL,
        data={**test_file_params, "youtube_url": test_youtube_url},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_creating_job_with_file_and_youtube_url(
    client: TestClient,
    test_audio_file,
    test_file_params,
    test_youtube_url,
):
    response = client.post(
        CREATE_URL,
        data={**test_file_params, "youtube_url": test_youtube_url},
        files={
            "file": ("dripdrop.mp3", test_audio_file, "audio/mpeg"),
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_creating_job_with_no_file_and_no_youtube_url(
    client: TestClient, test_file_params
):
    response = client.post(CREATE_URL, data=test_file_params)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
