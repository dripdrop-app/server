from fastapi import status

from dripdrop.youtube.tests.test_base import YoutubeBaseTest

CATEGORIES_URL = "/api/youtube/videos/categories"


class GetCategoriesTestCase(YoutubeBaseTest):
    async def test_get_categories_when_not_logged_in(self):
        response = await self.client.get(CATEGORIES_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    async def test_get_categories_with_no_categories(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.get(CATEGORIES_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"categories": []})

    async def test_get_categories_with_no_videos(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        await self.create_youtube_channel(
            id="1", title="channel", thumbnail="thumbnail"
        )
        await self.create_youtube_video_category(id=1, name="category")
        response = await self.client.get(CATEGORIES_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"categories": []})

    async def test_get_categories_with_subscribed_channels(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        channel = await self.create_youtube_channel(
            id="1", title="channel", thumbnail="thumbnail"
        )
        await self.create_youtube_subscription(channel_id=channel.id, email=user.email)
        category = await self.create_youtube_video_category(id=1, name="category")
        await self.create_youtube_video(
            id="1",
            title="title",
            thumbnail="thumbnail",
            channel_id=channel.id,
            category_id=category.id,
        )
        response = await self.client.get(CATEGORIES_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {"categories": [{"id": category.id, "name": category.name}]},
        )

    async def test_get_categories_with_specific_channel(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        channel = await self.create_youtube_channel(
            id="1", title="channel", thumbnail="thumbnail"
        )
        category = await self.create_youtube_video_category(id=1, name="category")
        await self.create_youtube_video(
            id="1",
            title="title",
            thumbnail="thumbnail",
            channel_id=channel.id,
            category_id=category.id,
        )
        response = await self.client.get(
            CATEGORIES_URL, params={"channel_id": channel.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {"categories": [{"id": category.id, "name": category.name}]},
        )

    async def test_get_categories_with_distinct_results(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        channel = await self.create_youtube_channel(
            id="1", title="channel", thumbnail="thumbnail"
        )
        category = await self.create_youtube_video_category(id=1, name="category")
        await self.create_youtube_video(
            id="1",
            title="title",
            thumbnail="thumbnail",
            channel_id=channel.id,
            category_id=category.id,
        )
        await self.create_youtube_video(
            id="2",
            title="title_2",
            thumbnail="thumbnail",
            channel_id=channel.id,
            category_id=category.id,
        )
        response = await self.client.get(
            CATEGORIES_URL, params={"channel_id": channel.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {"categories": [{"id": category.id, "name": category.name}]},
        )

    async def test_get_categories_with_multiple_results_in_ascending_name_order(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        channel = await self.create_youtube_channel(
            id="1", title="channel", thumbnail="thumbnail"
        )
        categories = [
            await self.create_youtube_video_category(id=i, name=f"category_{i}")
            for i in range(5)
        ]
        for i in range(5):
            await self.create_youtube_video(
                id=str(i),
                title=f"title_{i}",
                thumbnail="thumbnail",
                channel_id=channel.id,
                category_id=categories[i].id,
            )
        response = await self.client.get(
            CATEGORIES_URL, params={"channel_id": channel.id}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "categories": list(
                    map(
                        lambda category: {"id": category.id, "name": category.name},
                        categories,
                    )
                )
            },
        )
