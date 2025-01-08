from datetime import datetime

from fastapi import status

from dripdrop.music.tests.test_base import MusicBaseTest
from dripdrop.settings import settings

JOBS_URL = "/api/music/jobs"


class GetJobsTestCase(MusicBaseTest):
    async def test_jobs_when_not_logged_in(self):
        response = await self.client.get(f"{JOBS_URL}/1/10")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    async def test_jobs_with_no_results(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.get(f"{JOBS_URL}/1/10")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"totalPages": 0, "musicJobs": []})

    async def test_jobs_with_out_of_range_page(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        for i in range(2):
            await self.create_music_job(
                id=str(i),
                email=user.email,
                title="title",
                artist="artist",
                album="album",
            )
        response = await self.client.get(f"{JOBS_URL}/3/1")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    async def test_jobs_with_single_result(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        music_job = await self.create_music_job(
            id="1",
            email=user.email,
            title="title",
            artist="artist",
            album="album",
        )
        response = await self.client.get(f"{JOBS_URL}/1/10")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "totalPages": 1,
                "musicJobs": [
                    {
                        "id": music_job.id,
                        "artworkUrl": music_job.artwork_url,
                        "artworkFilename": music_job.artwork_filename,
                        "originalFilename": music_job.original_filename,
                        "filenameUrl": music_job.filename_url,
                        "videoUrl": music_job.video_url,
                        "downloadFilename": music_job.download_filename,
                        "downloadUrl": music_job.download_url,
                        "title": music_job.title,
                        "artist": music_job.artist,
                        "album": music_job.album,
                        "grouping": music_job.grouping,
                        "completed": music_job.completed,
                        "failed": music_job.failed,
                        "createdAt": self.convert_to_time_string(music_job.created_at),
                    }
                ],
            },
        )

    async def test_jobs_with_multiple_pages(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        music_jobs = [
            await self.create_music_job(
                id=str(i),
                email=user.email,
                title=f"title_{i}",
                artist="artist",
                album="album",
            )
            for i in range(5)
        ]
        music_jobs.sort(key=lambda music_job: music_job.created_at, reverse=True)
        response = await self.client.get(f"{JOBS_URL}/2/2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "totalPages": 3,
                "musicJobs": list(
                    map(
                        lambda music_job: {
                            "id": music_job.id,
                            "artworkUrl": music_job.artwork_url,
                            "artworkFilename": music_job.artwork_filename,
                            "originalFilename": music_job.original_filename,
                            "filenameUrl": music_job.filename_url,
                            "videoUrl": music_job.video_url,
                            "downloadFilename": music_job.download_filename,
                            "downloadUrl": music_job.download_url,
                            "title": music_job.title,
                            "artist": music_job.artist,
                            "album": music_job.album,
                            "grouping": music_job.grouping,
                            "completed": music_job.completed,
                            "failed": music_job.failed,
                            "createdAt": self.convert_to_time_string(
                                music_job.created_at
                            ),
                        },
                        music_jobs[2:4],
                    )
                ),
            },
        )

    async def test_jobs_with_deleted_jobs(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        music_jobs = [
            await self.create_music_job(
                id=str(i),
                email=user.email,
                title=f"title_{i}",
                artist="artist",
                album="album",
                deleted_at=datetime.now(tz=settings.timezone) if i % 2 else None,
            )
            for i in range(4)
        ]
        music_jobs = list(
            filter(lambda music_job: not music_job.deleted_at, music_jobs)
        )
        music_jobs.sort(key=lambda music_job: music_job.created_at, reverse=True)
        response = await self.client.get(f"{JOBS_URL}/1/4")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "totalPages": 1,
                "musicJobs": list(
                    map(
                        lambda music_job: {
                            "id": music_job.id,
                            "artworkUrl": music_job.artwork_url,
                            "artworkFilename": music_job.artwork_filename,
                            "originalFilename": music_job.original_filename,
                            "filenameUrl": music_job.filename_url,
                            "videoUrl": music_job.video_url,
                            "downloadFilename": music_job.download_filename,
                            "downloadUrl": music_job.download_url,
                            "title": music_job.title,
                            "artist": music_job.artist,
                            "album": music_job.album,
                            "grouping": music_job.grouping,
                            "completed": music_job.completed,
                            "failed": music_job.failed,
                            "createdAt": self.convert_to_time_string(
                                music_job.created_at
                            ),
                        },
                        music_jobs,
                    )
                ),
            },
        )

    async def test_jobs_only_for_logged_in_user(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        other_user = await self.create_user(
            email="other@gmail.com", password="password"
        )
        music_job = await self.create_music_job(
            id="1",
            email=user.email,
            title="title_1",
            artist="artist",
            album="album",
        )
        await self.create_music_job(
            id="2",
            email=other_user.email,
            title="title_2",
            artist="artist",
            album="album",
        )
        response = await self.client.get(f"{JOBS_URL}/1/4")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "totalPages": 1,
                "musicJobs": [
                    {
                        "id": music_job.id,
                        "artworkUrl": music_job.artwork_url,
                        "artworkFilename": music_job.artwork_filename,
                        "originalFilename": music_job.original_filename,
                        "filenameUrl": music_job.filename_url,
                        "videoUrl": music_job.video_url,
                        "downloadFilename": music_job.download_filename,
                        "downloadUrl": music_job.download_url,
                        "title": music_job.title,
                        "artist": music_job.artist,
                        "album": music_job.album,
                        "grouping": music_job.grouping,
                        "completed": music_job.completed,
                        "failed": music_job.failed,
                        "createdAt": self.convert_to_time_string(music_job.created_at),
                    }
                ],
            },
        )

    async def test_jobs_are_in_descending_order(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        music_jobs = [
            await self.create_music_job(
                id=str(i),
                email=user.email,
                title=f"title_{i}",
                artist="artist",
                album="album",
            )
            for i in range(4)
        ]
        music_jobs.sort(key=lambda music_job: music_job.created_at, reverse=True)
        response = await self.client.get(f"{JOBS_URL}/1/4")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "totalPages": 1,
                "musicJobs": list(
                    map(
                        lambda music_job: {
                            "id": music_job.id,
                            "artworkUrl": music_job.artwork_url,
                            "artworkFilename": music_job.artwork_filename,
                            "originalFilename": music_job.original_filename,
                            "filenameUrl": music_job.filename_url,
                            "videoUrl": music_job.video_url,
                            "downloadFilename": music_job.download_filename,
                            "downloadUrl": music_job.download_url,
                            "title": music_job.title,
                            "artist": music_job.artist,
                            "album": music_job.album,
                            "grouping": music_job.grouping,
                            "completed": music_job.completed,
                            "failed": music_job.failed,
                            "createdAt": self.convert_to_time_string(
                                music_job.created_at
                            ),
                        },
                        music_jobs,
                    )
                ),
            },
        )
