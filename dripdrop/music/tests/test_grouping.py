from fastapi import status
from unittest import skip

from dripdrop.music.tests.test_base import MusicBaseTest

GROUPING_URL = "/api/music/grouping"


@skip("Invidious can no longer retrieve youtube video info")
class GetGroupingTestCase(MusicBaseTest):
    async def test_grouping_when_not_logged_in(self):
        response = await self.client.get(
            GROUPING_URL,
            params={"video_url": "https://www.youtube.com/watch?v=FCrJNvJ-NIU"},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    async def test_grouping_with_invalid_video_url(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.get(
            GROUPING_URL, params={"video_url": "https://invalidurl"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    async def test_grouping_with_valid_video_url(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.get(
            GROUPING_URL,
            params={"video_url": "https://www.youtube.com/watch?v=FCrJNvJ-NIU"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"grouping": "Food Dip"})
