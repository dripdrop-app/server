from fastapi import status

from dripdrop.music.tests.test_base import MusicBaseTest

ARTWORK_URL = "/api/music/artwork"


class GetArtworkTestCase(MusicBaseTest):
    async def test_artwork_when_not_logged_in(self):
        response = await self.client.get(
            ARTWORK_URL,
            params={"artwork_url": "https://testimage.jpeg"},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    async def test_artwork_with_invalid_url(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.get(
            ARTWORK_URL, params={"artwork_url": "https://invalidurl"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    async def test_artwork_with_valid_image_url(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.get(
            ARTWORK_URL,
            params={"artwork_url": self.test_image_url},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"resolvedArtworkUrl": self.test_image_url})

    async def test_artwork_with_valid_soundcloud_url(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.get(
            ARTWORK_URL,
            params={
                "artwork_url": "https://soundcloud.com/badbunny15/bad-bunny-buscabulla-andrea"
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertRegex(
            json.get("resolvedArtworkUrl"),
            r"https:\/\/i1\.sndcdn\.com\/artworks-[a-zA-Z0-9]+-0-t500x500\.jpg",
        )
