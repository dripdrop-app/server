import requests
from ...conftest import APIEndpoints, TEST_EMAIL
from dripdrop.music.models import MusicJobs, MusicJob
from dripdrop.services.boto3 import boto3_service, Boto3Service
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.engine import Connection


class MusicJobEndpoints:
    base_url = f"{APIEndpoints.base_path}/music/jobs"
    jobs = f"{base_url}/1/1"
    listen = f"{base_url}/listen"
    create_youtube = f"{base_url}/create/youtube"
    create_file = f"{base_url}/create/file"
    delete_job = f"{base_url}/delete"


class TestCreateFileJob:
    def test_creating_file_job_with_invalid_file(self, client: TestClient):
        response = requests.get(
            "https://dripdrop-space.nyc3.digitaloceanspaces.com/artwork/dripdrop.png"
        )
        file = response.content
        response = client.post(
            MusicJobEndpoints.create_file,
            data={
                "title": "test",
                "artist": "test artist",
                "album": "test album",
                "grouping": "test grouping",
            },
            files={
                "file": ("dripdrop.png", file, response.headers.get("content-type")),
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_creating_file_job_with_valid_file(
        self, client: TestClient, db: Connection
    ):
        response = requests.get(
            "https://dripdrop-space-test.nyc3.digitaloceanspaces.com/test/07%20tun%20suh.mp3"
        )
        file = response.content
        response = client.post(
            MusicJobEndpoints.create_file,
            data={
                "title": "test",
                "artist": "test artist",
                "album": "test album",
                "grouping": "test grouping",
            },
            files={
                "file": ("tun suh.mp3", file, response.headers.get("content-type")),
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        results = db.execute(
            select(MusicJobs).where(MusicJobs.user_email == TEST_EMAIL)
        )
        rows = results.fetchall()
        assert len(rows) == 1
        job = MusicJob.from_orm(rows[0])
        boto3_service.delete_file(
            bucket=Boto3Service.S3_MUSIC_BUCKET, filename=f"{job.id}/{job.filename}"
        )
