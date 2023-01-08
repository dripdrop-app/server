from fastapi import status
from fastapi.testclient import TestClient

CREATE_URL = "/api/music/jobs/create"


def test_creating_file_job_with_invalid_content_type(
    client: TestClient, test_audio_file, test_file_params
):
    response = client.post(
        CREATE_URL,
        data=test_file_params,
        files={
            "file": ("tun suh.mp3", test_audio_file, "image/png"),
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_creating_file_job_with_invalid_file(
    client: TestClient, test_image_file, test_file_params, assert_job, run_worker
):
    response = client.post(
        CREATE_URL,
        data=test_file_params,
        files={
            "file": ("dripdrop.mp3", test_image_file, "audio/mpeg"),
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert_job(
        title=test_file_params["title"],
        artist=test_file_params["artist"],
        album=test_file_params["album"],
        grouping=test_file_params["grouping"],
        completed=False,
        failed=True,
    )


def test_creating_file_job_with_valid_file(
    client: TestClient, test_audio_file, test_file_params, assert_job, run_worker
):
    response = client.post(
        CREATE_URL,
        data=test_file_params,
        files={
            "file": ("tun suh.mp3", test_audio_file, "audio/mpeg"),
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert_job(
        title=test_file_params["title"],
        artist=test_file_params["artist"],
        album=test_file_params["album"],
        grouping=test_file_params["grouping"],
        completed=True,
        failed=False,
    )


def test_creating_file_job_with_valid_file_and_artwork_url(
    client: TestClient,
    test_audio_file,
    test_image_file,
    test_file_params,
    test_image_url,
    assert_job,
    run_worker,
):
    response = client.post(
        CREATE_URL,
        data={**test_file_params, "artwork_url": test_image_url},
        files={
            "file": ("tun suh.mp3", test_audio_file, "audio/mpeg"),
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert_job(
        title=test_file_params["title"],
        artist=test_file_params["artist"],
        album=test_file_params["album"],
        grouping=test_file_params["grouping"],
        artwork=test_image_file,
        completed=True,
        failed=False,
    )


def test_creating_file_job_with_valid_file_and_base64_artwork(
    client: TestClient,
    test_audio_file,
    test_image_file,
    test_file_params,
    test_base64_image,
    assert_job,
    run_worker,
):
    response = client.post(
        CREATE_URL,
        data={**test_file_params, "artwork_url": test_base64_image},
        files={
            "file": ("tun suh.mp3", test_audio_file, "audio/mpeg"),
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert_job(
        title=test_file_params["title"],
        artist=test_file_params["artist"],
        album=test_file_params["album"],
        grouping=test_file_params["grouping"],
        artwork=test_image_file,
        completed=True,
        failed=False,
    )
