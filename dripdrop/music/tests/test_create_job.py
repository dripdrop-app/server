from fastapi import status
from unittest import skip

from dripdrop.music.tests.test_base import MusicBaseTest

CREATE_URL = "/api/music/job/create"


@skip("Invidious can no longer download youtube videos")
class CreateMusicJobTestCase(MusicBaseTest):
    async def test_creating_music_job_when_not_logged_in(self):
        response = await self.client.post(
            CREATE_URL,
            data={
                "title": "title",
                "artist": "artist",
                "album": "album",
                "grouping": "grouping",
                "video_url": self.test_video_url,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    async def test_creating_music_job_with_file_and_video_url(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.post(
            CREATE_URL,
            data={
                "title": "title",
                "artist": "artist",
                "album": "album",
                "grouping": "grouping",
                "video_url": self.test_video_url,
            },
            files={
                "file": ("dripdrop.mp3", MusicBaseTest.test_audio_file, "audio/mpeg"),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    async def test_creating_music_job_with_no_file_and_no_video_url(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.post(
            CREATE_URL,
            data={
                "title": "title",
                "artist": "artist",
                "album": "album",
                "grouping": "grouping",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)


@skip("Invidious can no longer download youtube videos")
class CreateMusicFileJobTestCase(MusicBaseTest):
    async def test_creating_music_file_job_with_invalid_content_type(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.post(
            CREATE_URL,
            data={
                "title": "title",
                "artist": "artist",
                "album": "album",
                "grouping": "grouping",
            },
            files={
                "file": ("tun suh.mp3", MusicBaseTest.test_audio_file, "image/png"),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    async def test_creating_music_file_job_with_invalid_file(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        response = await self.client.post(
            CREATE_URL,
            data={
                "title": "title",
                "artist": "artist",
                "album": "album",
                "grouping": "grouping",
            },
            files={
                "file": ("dripdrop.mp3", MusicBaseTest.test_image_file, "audio/mpeg"),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        json = response.json()
        job = await self.get_music_job(email=user.email, music_job_id=json.get("id"))
        self.assertEqual(job.title, "title")
        self.assertEqual(job.artist, "artist")
        self.assertEqual(job.album, "album")
        self.assertEqual(job.grouping, "grouping")
        self.assertFalse(job.completed)
        self.assertTrue(job.failed)

    async def test_creating_music_file_job_with_valid_file(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        response = await self.client.post(
            CREATE_URL,
            data={
                "title": "title",
                "artist": "artist",
                "album": "album",
                "grouping": "grouping",
            },
            files={
                "file": ("tun suh.mp3", MusicBaseTest.test_audio_file, "audio/mpeg"),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        json = response.json()
        job = await self.get_music_job(email=user.email, music_job_id=json.get("id"))
        self.assertEqual(job.title, "title")
        self.assertEqual(job.artist, "artist")
        self.assertEqual(job.album, "album")
        self.assertEqual(job.grouping, "grouping")
        self.assertTrue(job.completed)
        self.assertFalse(job.failed)
        self.assertIsNotNone(job.filename_url)
        response = await self.http_client.get(job.filename_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(job.download_url)
        response = await self.http_client.get(job.download_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    async def test_creating_music_file_job_with_valid_file_and_artwork_url(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        response = await self.client.post(
            CREATE_URL,
            data={
                "title": "title",
                "artist": "artist",
                "album": "album",
                "grouping": "grouping",
                "artwork_url": self.test_image_url,
            },
            files={
                "file": ("tun suh.mp3", MusicBaseTest.test_audio_file, "audio/mpeg"),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        json = response.json()
        job = await self.get_music_job(email=user.email, music_job_id=json.get("id"))
        self.assertEqual(job.title, "title")
        self.assertEqual(job.artist, "artist")
        self.assertEqual(job.album, "album")
        self.assertEqual(job.grouping, "grouping")
        self.assertTrue(job.completed)
        self.assertFalse(job.failed)
        self.assertIsNotNone(job.filename_url)
        response = await self.http_client.get(job.filename_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(job.download_url)
        response = await self.http_client.get(job.download_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    async def test_creating_music_file_job_with_valid_file_and_base64_artwork(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        response = await self.client.post(
            CREATE_URL,
            data={
                "title": "title",
                "artist": "artist",
                "album": "album",
                "grouping": "grouping",
                "artwork_url": MusicBaseTest.test_base64_image,
            },
            files={
                "file": ("tun suh.mp3", MusicBaseTest.test_audio_file, "audio/mpeg"),
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        json = response.json()
        job = await self.get_music_job(email=user.email, music_job_id=json.get("id"))
        self.assertEqual(job.title, "title")
        self.assertEqual(job.artist, "artist")
        self.assertEqual(job.album, "album")
        self.assertEqual(job.grouping, "grouping")
        self.assertTrue(job.completed)
        self.assertFalse(job.failed)
        self.assertIsNotNone(job.filename_url)
        response = await self.http_client.get(job.filename_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(job.artwork_url)
        response = await self.http_client.get(job.artwork_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(job.download_url)
        response = await self.http_client.get(job.download_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


@skip("Invidious can no longer download youtube videos")
class CreateMusicVideoJobTestCase(MusicBaseTest):
    async def test_creating_music_video_job_with_invalid_video_url(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.post(
            CREATE_URL,
            data={
                "title": "title",
                "artist": "artist",
                "album": "album",
                "grouping": "grouping",
                "video_url": "not_valid",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    async def test_creating_music_video_job_with_valid_video_url(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        response = await self.client.post(
            CREATE_URL,
            data={
                "title": "title",
                "artist": "artist",
                "album": "album",
                "grouping": "grouping",
                "video_url": self.test_video_url,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        json = response.json()
        job = await self.get_music_job(email=user.email, music_job_id=json.get("id"))
        self.assertEqual(job.title, "title")
        self.assertEqual(job.artist, "artist")
        self.assertEqual(job.album, "album")
        self.assertEqual(job.grouping, "grouping")
        self.assertTrue(job.completed)
        self.assertFalse(job.failed)
        self.assertIsNotNone(job.download_url)
        response = await self.http_client.get(job.download_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    async def test_creating_music_video_job_with_valid_video_url_and_artwork_url(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        response = await self.client.post(
            CREATE_URL,
            data={
                "title": "title",
                "artist": "artist",
                "album": "album",
                "grouping": "grouping",
                "video_url": self.test_video_url,
                "artwork_url": self.test_image_url,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        json = response.json()
        job = await self.get_music_job(email=user.email, music_job_id=json.get("id"))
        self.assertEqual(job.title, "title")
        self.assertEqual(job.artist, "artist")
        self.assertEqual(job.album, "album")
        self.assertEqual(job.grouping, "grouping")
        self.assertTrue(job.completed)
        self.assertFalse(job.failed)
        self.assertIsNotNone(job.artwork_url)
        response = await self.http_client.get(job.artwork_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(job.download_url)
        response = await self.http_client.get(job.download_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    async def test_creating_music_video_job_with_valid_video_url_and_base64_artwork(
        self,
    ):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        response = await self.client.post(
            CREATE_URL,
            data={
                "title": "title",
                "artist": "artist",
                "album": "album",
                "grouping": "grouping",
                "video_url": self.test_video_url,
                "artwork_url": MusicBaseTest.test_base64_image,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        json = response.json()
        job = await self.get_music_job(email=user.email, music_job_id=json.get("id"))
        self.assertEqual(job.title, "title")
        self.assertEqual(job.artist, "artist")
        self.assertEqual(job.album, "album")
        self.assertEqual(job.grouping, "grouping")
        self.assertTrue(job.completed)
        self.assertFalse(job.failed)
        self.assertIsNotNone(job.artwork_url)
        response = await self.http_client.get(job.artwork_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(job.download_url)
        response = await self.http_client.get(job.download_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
