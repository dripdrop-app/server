from fastapi import status
from fastapi.testclient import TestClient

CREATE_URL = "/api/music/jobs/create"


def test_creating_youtube_job_with_invalid_youtube_url(
    client: TestClient, test_file_params
):
    response = client.post(
        CREATE_URL,
        data={
            **test_file_params,
            "youtube_url": "https://www.youtube.com/invalidurl",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_creating_youtube_job_with_valid_youtube_url(
    client: TestClient, run_worker, test_file_params, test_youtube_url, assert_job
):
    response = client.post(
        CREATE_URL,
        data={**test_file_params, "youtube_url": test_youtube_url},
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


def test_creating_youtube_job_with_valid_youtube_url_and_artwork_url(
    client: TestClient,
    test_image_file,
    test_file_params,
    test_youtube_url,
    test_image_url,
    assert_job,
    run_worker,
):
    response = client.post(
        CREATE_URL,
        data={
            **test_file_params,
            "youtube_url": test_youtube_url,
            "artwork_url": test_image_url,
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


def test_creating_youtube_job_with_valid_youtube_url_and_base64_artwork(
    client: TestClient,
    test_image_file,
    test_file_params,
    test_youtube_url,
    test_base64_image,
    assert_job,
    run_worker,
):
    response = client.post(
        CREATE_URL,
        data={
            **test_file_params,
            "youtube_url": test_youtube_url,
            "artwork_url": test_base64_image,
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
