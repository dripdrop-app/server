import os
import requests
import time
from datetime import datetime
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.engine import Connection

from dripdrop.apps.music.models import MusicJob
from dripdrop.services.boto3 import boto3_service, Boto3Service
from dripdrop.services.audio_tag import AudioTagService

from .conftest import APIEndpoints, TEST_EMAIL


class MusicJobEndpoints:
    base_url = f"{APIEndpoints.base_path}/music/jobs"
    jobs = f"{base_url}/1/1"
    listen = f"{base_url}/listen"
    create_youtube = f"{base_url}/create/youtube"
    create_file = f"{base_url}/create/file"
    delete_job = f"{base_url}/delete"


def check_job_is_correct(db: Connection = ..., tags: dict = ...):
    job = None
    start_time = datetime.now()
    while True:
        results = db.execute(select(MusicJob).where(MusicJob.user_email == TEST_EMAIL))
        job: MusicJob | None = results.first()
        assert job is not None
        assert job.failed is not True
        current_time = datetime.now()
        duration = current_time - start_time
        assert duration.seconds < 240
        if job.completed:
            break
        time.sleep(1)

    response = requests.get(job.download_url)
    assert response.status_code == status.HTTP_200_OK

    with open("test.mp3", "wb") as file:
        file.write(response.content)

    audio_tag_service = AudioTagService("test.mp3")
    assert audio_tag_service.title == tags["title"]
    assert audio_tag_service.artist == tags["artist"]
    assert audio_tag_service.album == tags["album"]
    if tags.get("grouping"):
        assert audio_tag_service.grouping == tags["grouping"]

    os.remove("test.mp3")
    if job.original_filename:
        boto3_service.delete_file(
            bucket=Boto3Service.S3_MUSIC_BUCKET,
            filename=job.original_filename,
        )
    boto3_service.delete_file(
        bucket=Boto3Service.S3_MUSIC_BUCKET,
        filename=job.download_filename,
    )


test_file_params = {
    "title": "test",
    "artist": "test artist",
    "album": "test album",
    "grouping": "test grouping",
}


class TestCreateFileJob:
    def test_creating_file_job_with_invalid_file(
        self, client: TestClient, create_default_user
    ):
        response = requests.get(
            "https://dripdrop-space.nyc3.digitaloceanspaces.com/artwork/dripdrop.png"
        )
        file = response.content
        response = client.post(
            MusicJobEndpoints.create_file,
            data=test_file_params,
            files={
                "file": ("dripdrop.png", file, response.headers.get("content-type")),
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_creating_file_job_with_valid_file(
        self, client: TestClient, db: Connection, create_default_user, run_worker
    ):
        response = requests.get(
            "https://dripdrop-space-test.nyc3.digitaloceanspaces.com/test/07%20tun%20suh.mp3"
        )
        file = response.content
        response = client.post(
            MusicJobEndpoints.create_file,
            data=test_file_params,
            files={
                "file": ("tun suh.mp3", file, response.headers.get("content-type")),
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        check_job_is_correct(db=db, tags=test_file_params)


class TestCreateYoutubeJob:
    def test_creating_youtube_job_with_invalid_youtube_url(
        self, client: TestClient, create_default_user
    ):
        response = client.post(
            MusicJobEndpoints.create_youtube,
            data={
                **test_file_params,
                "youtube_url": "https://www.youtube.com/invalidurl",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_creating_youtube_job_with_valid_youtube_url(
        self, client: TestClient, db: Connection, create_default_user, run_worker
    ):
        response = client.post(
            MusicJobEndpoints.create_youtube,
            data={
                **test_file_params,
                "youtube_url": "https://www.youtube.com/watch?v=wX49jNyqq04",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        check_job_is_correct(db=db, tags=test_file_params)
