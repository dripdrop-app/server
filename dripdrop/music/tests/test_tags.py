from fastapi import status

from dripdrop.music.tests.test_base import MusicBaseTest

TAGS_URL = "/api/music/tags"


class GetTagsTestCase(MusicBaseTest):
    async def test_tags_when_not_logged_in(self):
        response = await self.client.post(TAGS_URL, files={"file": b"test"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    async def test_tags_with_an_invalid_file(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.http_client.get(
            "https://dripdrop-space.nyc3.digitaloceanspaces.com/artwork/dripdrop.png"
        )
        file = response.content
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = await self.client.post(TAGS_URL, files={"file": file})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "title": None,
                "artist": None,
                "album": None,
                "grouping": None,
                "artworkUrl": None,
            },
        )

    async def test_tags_with_a_mp3_without_tags(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.http_client.get(
            "https://dripdrop-space-test.nyc3.digitaloceanspaces.com/test/sample4.mp3"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        file = response.content
        response = await self.client.post(TAGS_URL, files={"file": file})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "title": None,
                "artist": None,
                "album": None,
                "grouping": None,
                "artworkUrl": None,
            },
        )

    async def test_tags_with_a_valid_mp3_file(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.http_client.get(
            "https://dripdrop-space-test.nyc3.digitaloceanspaces.com/"
            + "test/Criminal%20Sinny%20&%20Fako.mp3"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        file = response.content
        tags = await self.get_tags_from_file(file=file)
        response = await self.client.post(TAGS_URL, files={"file": file})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "title": "Criminal",
                "artist": "Sinny & Fako",
                "album": "Criminal - Single",
                "grouping": "Tribal Trap",
                "artworkUrl": tags.get_artwork_as_base64(),
            },
        )
