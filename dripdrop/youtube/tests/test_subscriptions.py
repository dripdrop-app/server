from datetime import datetime
from fastapi import status
from unittest.mock import patch

from dripdrop.settings import settings
from dripdrop.youtube.tests.test_base import YoutubeBaseTest

SUBSCRIPTIONS_URL = "/api/youtube/subscriptions"


class GetSubscriptionsTestCase(YoutubeBaseTest):
    async def test_get_subscriptions_when_not_logged_in(self):
        response = await self.client.get(f"{SUBSCRIPTIONS_URL}/1/10")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    async def test_get_subscriptions_with_no_results(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.get(f"{SUBSCRIPTIONS_URL}/1/10")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"totalPages": 0, "subscriptions": []})

    async def test_get_subscriptions_out_of_range_page(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        channel = await self.create_youtube_channel(
            id="1", title="channel", thumbnail="thumbnail"
        )
        await self.create_youtube_subscription(channel_id=channel.id, email=user.email)
        response = await self.client.get(f"{SUBSCRIPTIONS_URL}/2/1")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    async def test_get_subscriptions_with_single_result(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        channel = await self.create_youtube_channel(
            id="1", title="channel", thumbnail="thumbnail"
        )
        await self.create_youtube_subscription(channel_id=channel.id, email=user.email)
        response = await self.client.get(f"{SUBSCRIPTIONS_URL}/1/1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "totalPages": 1,
                "subscriptions": [
                    {
                        "channelId": channel.id,
                        "channelTitle": channel.title,
                        "channelThumbnail": channel.thumbnail,
                    }
                ],
            },
        )

    async def test_get_subscriptions_with_deleted_subscription(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        channel = await self.create_youtube_channel(
            id="1", title="channel", thumbnail="thumbnail"
        )
        other_channel = await self.create_youtube_channel(
            id="2", title="channel_2", thumbnail="thumbnail"
        )
        await self.create_youtube_subscription(channel_id=channel.id, email=user.email)
        await self.create_youtube_subscription(
            channel_id=other_channel.id,
            email=user.email,
            deleted_at=datetime.now(settings.timezone),
        )
        response = await self.client.get(f"{SUBSCRIPTIONS_URL}/1/1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "totalPages": 1,
                "subscriptions": [
                    {
                        "channelId": channel.id,
                        "channelTitle": channel.title,
                        "channelThumbnail": channel.thumbnail,
                    }
                ],
            },
        )

    async def test_get_subscriptions_with_multiple_pages(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        channels = [
            await self.create_youtube_channel(
                id=str(i),
                title=f"channel_{i}",
                thumbnail="thumbnail",
            )
            for i in range(3)
        ]
        for channel in channels:
            await self.create_youtube_subscription(
                channel_id=channel.id, email=user.email
            )
        response = await self.client.get(f"{SUBSCRIPTIONS_URL}/1/1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "totalPages": 3,
                "subscriptions": [
                    {
                        "channelId": channels[0].id,
                        "channelTitle": channels[0].title,
                        "channelThumbnail": channels[0].thumbnail,
                    }
                ],
            },
        )

    async def test_get_subscriptions_for_logged_in_account(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        other_user = await self.create_user(
            email="otheruser@gmail.com", password="password"
        )
        channel = await self.create_youtube_channel(
            id="1",
            title="channel_1",
            thumbnail="thumbnail",
        )
        other_channel = await self.create_youtube_channel(
            id="2",
            title="channel_2",
            thumbnail="thumbnail",
        )
        await self.create_youtube_subscription(
            channel_id=other_channel.id, email=other_user.email
        )
        await self.create_youtube_subscription(channel_id=channel.id, email=user.email)
        response = await self.client.get(f"{SUBSCRIPTIONS_URL}/1/2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "totalPages": 1,
                "subscriptions": [
                    {
                        "channelId": channel.id,
                        "channelTitle": channel.title,
                        "channelThumbnail": channel.thumbnail,
                    }
                ],
            },
        )

    async def test_get_subscriptions_are_in_descending_order_by_title(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        channels = [
            await self.create_youtube_channel(
                id=str(i),
                title=f"channel_{i}",
                thumbnail="thumbnail",
            )
            for i in range(3)
        ]
        subscriptions = [
            await self.create_youtube_subscription(
                channel_id=channel.id, email=user.email
            )
            for channel in channels
        ]
        channels.sort(key=lambda channel: channel.title)
        subscriptions = list(
            map(
                lambda channel: next(
                    filter(
                        lambda subscription: channel.id == subscription.channel_id,
                        subscriptions,
                    )
                ),
                channels,
            )
        )
        response = await self.client.get(f"{SUBSCRIPTIONS_URL}/1/3")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "totalPages": 1,
                "subscriptions": list(
                    map(
                        lambda i: {
                            "channelId": channels[i].id,
                            "channelTitle": channels[i].title,
                            "channelThumbnail": channels[i].thumbnail,
                        },
                        range(len(subscriptions)),
                    )
                ),
            },
        )


class CreateSubscriptionTestCase(YoutubeBaseTest):
    async def test_add_user_subscription_when_not_logged_in(self):
        response = await self.client.put(
            f"{SUBSCRIPTIONS_URL}/user", params={"channel_id": "1"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    async def test_add_user_subscription_with_nonexistent_channel_in_database(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.put(
            f"{SUBSCRIPTIONS_URL}/user", params={"channel_id": "1"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("dripdrop.services.rq_client.default.enqueue")
    async def test_add_user_subscription_with_channel_in_database(self, _):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        channel = await self.create_youtube_channel(
            id="UCCuIpl5564hhP8Qpucvu7RA",
            title="Food Dip",
            thumbnail="thumbnail",
        )
        response = await self.client.put(
            f"{SUBSCRIPTIONS_URL}/user", params={"channel_id": channel.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "channelId": channel.id,
                "channelTitle": channel.title,
                "channelThumbnail": channel.thumbnail,
            },
        )

    async def test_add_user_subscription_with_nonexistent_channel_on_youtube(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.put(
            f"{SUBSCRIPTIONS_URL}/user", params={"channel_id": "1"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("dripdrop.services.rq_client.default.enqueue")
    async def test_add_user_subscription_with_channel_on_youtube(self, _):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.put(
            f"{SUBSCRIPTIONS_URL}/user",
            params={"channel_id": "UCCuIpl5564hhP8Qpucvu7RA"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(json.get("channelId"), "UCCuIpl5564hhP8Qpucvu7RA")
        self.assertEqual(json.get("channelTitle"), "Food Dip")
        self.assertIsNotNone(json.get("channelThumbnail"))

    async def test_add_user_subscription_with_nonexistent_channel_handle_on_youtube(
        self,
    ):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.put(
            f"{SUBSCRIPTIONS_URL}/user",
            params={"channel_id": "@dripdrop-channel-non-existent"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("dripdrop.services.rq_client.default.enqueue")
    async def test_add_user_subscription_with_channel_handle_on_youtube(self, _):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.put(
            f"{SUBSCRIPTIONS_URL}/user", params={"channel_id": "@TDBarrett"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json = response.json()
        self.assertEqual(json.get("channelId"), "UCYdHjl9aX-8Fwyg0OBOL21g")
        self.assertEqual(json.get("channelTitle"), "TDBarrett")
        self.assertIsNotNone(json.get("channelThumbnail"))

    async def test_add_user_subscription_when_subscription_exists(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        channel = await self.create_youtube_channel(
            id="UC_ZYORKR3s_0qL5CuySVSPA",
            title="dripdrop-channel",
            thumbnail="thumbnail",
        )
        await self.create_youtube_subscription(channel_id=channel.id, email=user.email)
        response = await self.client.put(
            f"{SUBSCRIPTIONS_URL}/user", params={"channel_id": channel.id}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("dripdrop.services.rq_client.default.enqueue")
    async def test_add_user_subscription_with_deleted_subscription(self, _):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        channel = await self.create_youtube_channel(
            id="UC_ZYORKR3s_0qL5CuySVSPA",
            title="dripdrop-channel",
            thumbnail="thumbnail",
        )
        await self.create_youtube_subscription(
            channel_id=channel.id,
            email=user.email,
            deleted_at=datetime.now(settings.timezone),
        )
        response = await self.client.put(
            f"{SUBSCRIPTIONS_URL}/user", params={"channel_id": channel.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "channelId": channel.id,
                "channelTitle": channel.title,
                "channelThumbnail": channel.thumbnail,
            },
        )


class DeleteSubscriptionTestCase(YoutubeBaseTest):
    async def test_delete_user_subscription_when_not_logged_in(self):
        response = await self.client.delete(
            f"{SUBSCRIPTIONS_URL}/user", params={"channel_id": "1"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    async def test_delete_user_subscription_with_nonexistent_subscription(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.delete(
            f"{SUBSCRIPTIONS_URL}/user", params={"channel_id": "1"}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    async def test_delete_user_subscription(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        channel = await self.create_youtube_channel(
            id="1",
            title="channel_1",
            thumbnail="thumbnail",
        )
        await self.create_youtube_subscription(channel_id=channel.id, email=user.email)
        response = await self.client.delete(
            f"{SUBSCRIPTIONS_URL}/user", params={"channel_id": channel.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
