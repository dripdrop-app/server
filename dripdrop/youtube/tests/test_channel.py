from datetime import datetime, timedelta
from fastapi import status
from unittest.mock import patch

from dripdrop.settings import settings
from dripdrop.youtube.tests.test_base import YoutubeBaseTest

CHANNEL_URL = "/api/youtube/channel"


class GetChannelTestCase(YoutubeBaseTest):
    async def test_get_channels_when_not_logged_in(self):
        response = await self.client.get(f"{CHANNEL_URL}/test")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    async def test_get_channels_with_nonexistent_channel(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.get(f"{CHANNEL_URL}/test")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    async def test_get_channels(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        channel = await self.create_youtube_channel(
            id="1", title="channel", thumbnail="thumbnail"
        )
        response = await self.client.get(f"{CHANNEL_URL}/1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "id": channel.id,
                "title": channel.title,
                "thumbnail": channel.thumbnail,
                "subscribed": False,
                "updating": False,
            },
        )

    async def test_get_channels_with_subscription(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        channel = await self.create_youtube_channel(
            id="1", title="channel", thumbnail="thumbnail"
        )
        await self.create_youtube_subscription(channel_id=channel.id, email=user.email)
        response = await self.client.get(f"{CHANNEL_URL}/1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "id": channel.id,
                "title": channel.title,
                "thumbnail": channel.thumbnail,
                "subscribed": True,
                "updating": False,
            },
        )

    async def test_get_channels_with_deleted_subscription(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        channel = await self.create_youtube_channel(
            id="1", title="channel", thumbnail="thumbnail"
        )
        await self.create_youtube_subscription(
            channel_id=channel.id,
            email=user.email,
            deleted_at=datetime.now(settings.timezone),
        )
        response = await self.client.get(f"{CHANNEL_URL}/1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "id": channel.id,
                "title": channel.title,
                "thumbnail": channel.thumbnail,
                "subscribed": False,
                "updating": False,
            },
        )


class GetUserChannelTestCase(YoutubeBaseTest):
    async def test_get_user_youtube_channel_when_not_logged_in(self):
        response = await self.client.get(f"{CHANNEL_URL}/user")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    async def test_get_user_youtube_channel_with_nonexistent_channel(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.get(f"{CHANNEL_URL}/user")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    async def test_get_user_youtube_channel(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        await self.update_user_youtube_channel(id="1", email=user.email)
        response = await self.client.get(f"{CHANNEL_URL}/user")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"id": "1"})


class UpdateUserChannelTestCase(YoutubeBaseTest):
    async def test_update_user_channel_when_not_logged_in(self):
        response = await self.client.post(
            f"{CHANNEL_URL}/user", json={"channel_id": "2"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    async def test_update_user_channel_with_nonexistent_channel_on_youtube(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.post(
            f"{CHANNEL_URL}/user", json={"channel_id": "2"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("dripdrop.services.rq_client.default.enqueue")
    async def test_update_user_channel_from_nonexisting_channel_to_youtube_channel(
        self, _
    ):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.post(
            f"{CHANNEL_URL}/user", json={"channel_id": "UC_ZYORKR3s_0qL5CuySVSPA"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    async def test_update_user_channel_with_nonexistent_channel_handle_on_youtube(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.post(
            f"{CHANNEL_URL}/user", json={"channel_id": "@2"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("dripdrop.services.rq_client.default.enqueue")
    async def test_update_user_channel_from_nonexisting_channel_to_youtube_handle(
        self, _
    ):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.post(
            f"{CHANNEL_URL}/user", json={"channel_id": "@dripdrop-channel"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    async def test_update_user_channel_with_existing_channel_within_day(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        await self.update_user_youtube_channel(id="1", email=user.email)
        response = await self.client.post(
            f"{CHANNEL_URL}/user", json={"channel_id": "2"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("dripdrop.services.rq_client.default.enqueue")
    async def test_update_user_channel_with_existing_channel(self, _):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        await self.update_user_youtube_channel(
            id="UC_ZYORKR3s_0qL5CuySVSPA",
            email=user.email,
            modified_at=datetime.now(settings.timezone) - timedelta(days=2),
        )
        response = await self.client.post(
            f"{CHANNEL_URL}/user", json={"channel_id": "UCCuIpl5564hhP8Qpucvu7RA"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_channel = await self.get_user_youtube_channel(email=user.email)
        self.assertEqual(user_channel.id, "UCCuIpl5564hhP8Qpucvu7RA")
