import pytest
import time
from datetime import datetime, timezone
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.engine import Connection


@pytest.fixture(autouse=True)
def create_user(create_default_user):
    create_default_user(admin=False)


class MusicJobEndpoints:
    base_url = "/api/music/jobs"
    listen = f"{base_url}/listen"
    create_job = f"{base_url}/create"
    delete_job = f"{base_url}/delete"


class TestCreateJob:
    def test_creating_job_with_file_and_youtube_url(
        self, client: TestClient, test_audio_file, test_file_params, test_youtube_url
    ):
        response = client.post(
            MusicJobEndpoints.create_job,
            data={**test_file_params, "youtube_url": test_youtube_url},
            files={
                "file": ("dripdrop.mp3", test_audio_file, "audio/mpeg"),
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_creating_job_with_no_file_and_no_youtube_url(
        self, client: TestClient, test_file_params
    ):
        response = client.post(MusicJobEndpoints.create_job, data=test_file_params)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestCreateFileJob:
    def test_creating_file_job_with_invalid_content_type(
        self, client: TestClient, test_audio_file, test_file_params
    ):
        response = client.post(
            MusicJobEndpoints.create_job,
            data=test_file_params,
            files={
                "file": ("tun suh.mp3", test_audio_file, "image/png"),
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_creating_file_job_with_invalid_file(
        self,
        client: TestClient,
        db: Connection,
        run_worker,
        test_image_file,
        test_file_params,
        assert_job,
    ):
        response = client.post(
            MusicJobEndpoints.create_job,
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
        self,
        client: TestClient,
        db: Connection,
        run_worker,
        test_audio_file,
        test_file_params,
        assert_job,
    ):
        response = client.post(
            MusicJobEndpoints.create_job,
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
        self,
        client: TestClient,
        db: Connection,
        run_worker,
        test_audio_file,
        test_image_file,
        test_file_params,
        test_image_url,
        assert_job,
    ):
        response = client.post(
            MusicJobEndpoints.create_job,
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


class TestCreateYoutubeJob:
    def test_creating_youtube_job_with_invalid_youtube_url(
        self, client: TestClient, test_file_params
    ):
        response = client.post(
            MusicJobEndpoints.create_job,
            data={
                **test_file_params,
                "youtube_url": "https://www.youtube.com/invalidurl",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_creating_youtube_job_with_valid_youtube_url(
        self,
        client: TestClient,
        db: Connection,
        run_worker,
        test_file_params,
        test_youtube_url,
        assert_job,
    ):
        response = client.post(
            MusicJobEndpoints.create_job,
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
        self,
        client: TestClient,
        db: Connection,
        run_worker,
        test_image_file,
        test_file_params,
        test_youtube_url,
        test_image_url,
        assert_job,
    ):
        response = client.post(
            MusicJobEndpoints.create_job,
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


class TestGetJobs:
    def test_get_jobs_with_no_results(self, client: TestClient):
        response = client.get(f"{MusicJobEndpoints.base_url}/1/10")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_jobs_with_out_of_range_page(
        self, client: TestClient, create_music_job, test_music_job
    ):
        for i in range(15):
            create_music_job(**{**test_music_job, "id": f"test_{i}"})
        response = client.get(f"{MusicJobEndpoints.base_url}/3/10")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_jobs_with_single_result(
        self, client: TestClient, create_music_job, test_music_job, assert_jobs_response
    ):
        create_music_job(**test_music_job)
        response = client.get(f"{MusicJobEndpoints.base_url}/1/10")
        assert response.status_code == status.HTTP_200_OK
        assert_jobs_response(json=response.json(), jobs_length=1, total_pages=1)

    def test_get_jobs_with_partial_page(
        self, client: TestClient, create_music_job, test_music_job, assert_jobs_response
    ):
        for i in range(15):
            create_music_job(**{**test_music_job, "id": f"test_{i}"})
        response = client.get(f"{MusicJobEndpoints.base_url}/1/20")
        assert response.status_code == status.HTTP_200_OK
        assert_jobs_response(json=response.json(), jobs_length=15, total_pages=1)

    def test_get_jobs_with_multiple_pages(
        self, client: TestClient, create_music_job, test_music_job, assert_jobs_response
    ):
        for i in range(20):
            create_music_job(**{**test_music_job, "id": f"test_{i}"})
        response = client.get(f"{MusicJobEndpoints.base_url}/1/10")
        assert response.status_code == status.HTTP_200_OK
        assert_jobs_response(json=response.json(), jobs_length=10, total_pages=2)

    def test_get_jobs_with_deleted_jobs(
        self, client: TestClient, create_music_job, test_music_job, assert_jobs_response
    ):
        for i in range(10):
            create_music_job(
                **{
                    **test_music_job,
                    "id": f"test_{i}",
                    "deleted_at": datetime.now(timezone.utc) if i % 2 == 0 else None,
                }
            )
        response = client.get(f"{MusicJobEndpoints.base_url}/1/5")
        assert response.status_code == status.HTTP_200_OK
        assert_jobs_response(json=response.json(), jobs_length=5, total_pages=1)

    def test_get_jobs_are_in_descending_order(
        self, client: TestClient, create_music_job, test_music_job, assert_jobs_response
    ):
        for i in range(5):
            create_music_job(**{**test_music_job, "id": f"test_{i}"})
            time.sleep(1)
        response = client.get(f"{MusicJobEndpoints.base_url}/1/5")
        assert response.status_code == status.HTTP_200_OK
        assert_jobs_response(json=response.json(), jobs_length=5, total_pages=1)
        jobs = response.json()["jobs"]
        for i in range(1, len(jobs)):
            assert jobs[i]["createdAt"] < jobs[i - 1]["createdAt"]


# class ListenJobs:
#     def test_listen_for_running_job(self, client: TestClient):
#         with client.websocket_connect(MusicJobEndpoints.listen) as websocket:
#             while True:
