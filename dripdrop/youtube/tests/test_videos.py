from datetime import datetime
from fastapi import status

from dripdrop.settings import settings
from dripdrop.youtube.tests.test_base import YoutubeBaseTest

VIDEOS_URL = "/api/youtube/videos"
VIDEOS_QUEUE_URL = "/api/youtube/videos/queue"
VIDEOS_CATEGORIES_URL = "/api/youtube/videos/categories"


class GetVideosCategoriesTestCase(YoutubeBaseTest):
    async def test_get_categories_when_not_logged_in(self):
        response = await self.client.get(VIDEOS_CATEGORIES_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    async def test_get_categories_with_no_categories(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.get(VIDEOS_CATEGORIES_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"categories": []})

    async def test_get_categories_with_no_videos(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        await self.create_youtube_channel(
            id="1", title="channel", thumbnail="thumbnail"
        )
        await self.create_youtube_video_category(id=1, name="category")
        response = await self.client.get(VIDEOS_CATEGORIES_URL)
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
        response = await self.client.get(VIDEOS_CATEGORIES_URL)
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
            VIDEOS_CATEGORIES_URL, params={"channel_id": channel.id}
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
            VIDEOS_CATEGORIES_URL, params={"channel_id": channel.id}
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
            VIDEOS_CATEGORIES_URL, params={"channel_id": channel.id}
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


class GetVideosTestCase(YoutubeBaseTest):
    async def test_get_videos_when_not_logged_in(self):
        response = await self.client.get(f"{VIDEOS_URL}/1/10")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    async def test_get_videos_with_no_videos(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.get(f"{VIDEOS_URL}/1/10")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"totalPages": 0, "videos": []})

    async def test_get_videos_with_no_subscriptions(self):
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
        response = await self.client.get(f"{VIDEOS_URL}/1/10")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"totalPages": 0, "videos": []})

    async def test_get_videos_with_out_of_range_page(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.get(f"{VIDEOS_URL}/2/10")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    async def test_get_videos_with_single_result(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        channel = await self.create_youtube_channel(
            id="1", title="channel", thumbnail="thumbnail"
        )
        await self.create_youtube_subscription(channel_id=channel.id, email=user.email)
        category = await self.create_youtube_video_category(id=1, name="category")
        video = await self.create_youtube_video(
            id="1",
            title="title",
            thumbnail="thumbnail",
            channel_id=channel.id,
            category_id=category.id,
            description="1",
        )
        response = await self.client.get(f"{VIDEOS_URL}/1/10")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "totalPages": 1,
                "videos": [
                    {
                        "id": video.id,
                        "title": video.title,
                        "thumbnail": video.thumbnail,
                        "categoryId": category.id,
                        "categoryName": category.name,
                        "description": video.description,
                        "publishedAt": video.published_at.replace(
                            tzinfo=settings.timezone
                        ).isoformat(),
                        "channelId": channel.id,
                        "channelTitle": channel.title,
                        "channelThumbnail": channel.thumbnail,
                        "liked": None,
                        "queued": None,
                        "watched": None,
                    }
                ],
            },
        )

    async def test_get_videos_with_multiple_videos(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        channel = await self.create_youtube_channel(
            id="1", title="channel", thumbnail="thumbnail"
        )
        await self.create_youtube_subscription(channel_id=channel.id, email=user.email)
        category = await self.create_youtube_video_category(id=1, name="category")
        videos = [
            await self.create_youtube_video(
                id=str(i),
                title=f"title_{i}",
                thumbnail="thumbnail",
                channel_id=channel.id,
                category_id=category.id,
                description=str(i),
            )
            for i in range(5)
        ]
        videos.sort(key=lambda video: video.published_at, reverse=True)
        response = await self.client.get(f"{VIDEOS_URL}/1/5")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "totalPages": 1,
                "videos": list(
                    map(
                        lambda video: {
                            "id": video.id,
                            "title": video.title,
                            "thumbnail": video.thumbnail,
                            "categoryId": category.id,
                            "categoryName": category.name,
                            "description": video.description,
                            "publishedAt": video.published_at.replace(
                                tzinfo=settings.timezone
                            ).isoformat(),
                            "channelId": channel.id,
                            "channelTitle": channel.title,
                            "channelThumbnail": channel.thumbnail,
                            "liked": None,
                            "queued": None,
                            "watched": None,
                        },
                        videos,
                    )
                ),
            },
        )

    async def test_get_videos_with_multiple_pages(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        channel = await self.create_youtube_channel(
            id="1", title="channel", thumbnail="thumbnail"
        )
        await self.create_youtube_subscription(channel_id=channel.id, email=user.email)
        category = await self.create_youtube_video_category(id=1, name="category")
        videos = [
            await self.create_youtube_video(
                id=str(i),
                title=f"title_{i}",
                thumbnail="thumbnail",
                channel_id=channel.id,
                category_id=category.id,
                description=str(i),
            )
            for i in range(5)
        ]
        videos.sort(key=lambda video: video.published_at, reverse=True)
        response = await self.client.get(f"{VIDEOS_URL}/2/2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "totalPages": 3,
                "videos": list(
                    map(
                        lambda video: {
                            "id": video.id,
                            "title": video.title,
                            "thumbnail": video.thumbnail,
                            "categoryId": category.id,
                            "categoryName": category.name,
                            "description": video.description,
                            "publishedAt": video.published_at.replace(
                                tzinfo=settings.timezone
                            ).isoformat(),
                            "channelId": channel.id,
                            "channelTitle": channel.title,
                            "channelThumbnail": channel.thumbnail,
                            "liked": None,
                            "queued": None,
                            "watched": None,
                        },
                        videos[2:4],
                    )
                ),
            },
        )

    async def test_get_videos_in_descending_order_by_published_date(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        channel = await self.create_youtube_channel(
            id="1", title="channel", thumbnail="thumbnail"
        )
        await self.create_youtube_subscription(channel_id=channel.id, email=user.email)
        category = await self.create_youtube_video_category(id=1, name="category")
        videos = [
            await self.create_youtube_video(
                id=str(i),
                title=f"title_{i}",
                thumbnail="thumbnail",
                channel_id=channel.id,
                category_id=category.id,
                description=str(i),
            )
            for i in range(5)
        ]
        videos.sort(key=lambda video: video.published_at, reverse=True)
        response = await self.client.get(f"{VIDEOS_URL}/1/5")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "totalPages": 1,
                "videos": list(
                    map(
                        lambda video: {
                            "id": video.id,
                            "title": video.title,
                            "thumbnail": video.thumbnail,
                            "categoryId": category.id,
                            "categoryName": category.name,
                            "description": video.description,
                            "publishedAt": video.published_at.replace(
                                tzinfo=settings.timezone
                            ).isoformat(),
                            "channelId": channel.id,
                            "channelTitle": channel.title,
                            "channelThumbnail": channel.thumbnail,
                            "liked": None,
                            "queued": None,
                            "watched": None,
                        },
                        videos,
                    )
                ),
            },
        )

    async def test_get_videos_with_deleted_subscriptions(self):
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
        category = await self.create_youtube_video_category(id=1, name="category")
        await self.create_youtube_video(
            id="1",
            title="title",
            thumbnail="thumbnail",
            channel_id=channel.id,
            category_id=category.id,
        )
        response = await self.client.get(f"{VIDEOS_URL}/1/10")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"totalPages": 0, "videos": []})

    async def test_get_videos_with_watched_populated(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        other_user = await self.create_user(
            email="other@gmail.com", password="password"
        )
        channel = await self.create_youtube_channel(
            id="1", title="channel", thumbnail="thumbnail"
        )
        await self.create_youtube_subscription(channel_id=channel.id, email=user.email)
        await self.create_youtube_subscription(
            channel_id=channel.id, email=other_user.email
        )
        category = await self.create_youtube_video_category(id=1, name="category")
        watched_video = await self.create_youtube_video(
            id="1",
            title="title_1",
            thumbnail="thumbnail",
            channel_id=channel.id,
            category_id=category.id,
            description="1",
        )
        other_video = await self.create_youtube_video(
            id="2",
            title="title_2",
            thumbnail="thumbnail",
            channel_id=channel.id,
            category_id=category.id,
            description="2",
        )
        watch = await self.create_youtube_video_watch(
            email=user.email, video_id=watched_video.id
        )
        await self.create_youtube_video_watch(
            email=other_user.email, video_id=other_video.id
        )
        response = await self.client.get(f"{VIDEOS_URL}/1/5")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "totalPages": 1,
                "videos": [
                    {
                        "id": other_video.id,
                        "title": other_video.title,
                        "thumbnail": other_video.thumbnail,
                        "categoryId": category.id,
                        "categoryName": category.name,
                        "description": other_video.description,
                        "publishedAt": other_video.published_at.replace(
                            tzinfo=settings.timezone
                        ).isoformat(),
                        "channelId": channel.id,
                        "channelTitle": channel.title,
                        "channelThumbnail": channel.thumbnail,
                        "liked": None,
                        "queued": None,
                        "watched": None,
                    },
                    {
                        "id": watched_video.id,
                        "title": watched_video.title,
                        "thumbnail": watched_video.thumbnail,
                        "categoryId": category.id,
                        "categoryName": category.name,
                        "description": watched_video.description,
                        "publishedAt": watched_video.published_at.replace(
                            tzinfo=settings.timezone
                        ).isoformat(),
                        "channelId": channel.id,
                        "channelTitle": channel.title,
                        "channelThumbnail": channel.thumbnail,
                        "liked": None,
                        "queued": None,
                        "watched": watch.created_at.replace(
                            tzinfo=settings.timezone
                        ).isoformat(),
                    },
                ],
            },
        )

    async def test_get_videos_with_channel_id(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        channel = await self.create_youtube_channel(
            id="1", title="channel", thumbnail="thumbnail"
        )
        other_channel = await self.create_youtube_channel(
            id="2", title="channel", thumbnail="thumbnail"
        )
        category = await self.create_youtube_video_category(id=1, name="category")
        video = await self.create_youtube_video(
            id="1",
            title="title",
            thumbnail="thumbnail",
            channel_id=channel.id,
            category_id=category.id,
            description="1",
        )
        await self.create_youtube_video(
            id="2",
            title="title",
            thumbnail="thumbnail",
            channel_id=other_channel.id,
            category_id=category.id,
            description="2",
        )
        response = await self.client.get(
            f"{VIDEOS_URL}/1/10", params={"channel_id": "1"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "totalPages": 1,
                "videos": [
                    {
                        "id": video.id,
                        "title": video.title,
                        "thumbnail": video.thumbnail,
                        "categoryId": category.id,
                        "categoryName": category.name,
                        "description": video.description,
                        "publishedAt": video.published_at.replace(
                            tzinfo=settings.timezone
                        ).isoformat(),
                        "channelId": channel.id,
                        "channelTitle": channel.title,
                        "channelThumbnail": channel.thumbnail,
                        "liked": None,
                        "queued": None,
                        "watched": None,
                    }
                ],
            },
        )

    async def test_get_videos_with_specific_video_category(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        channel = await self.create_youtube_channel(
            id="1", title="channel", thumbnail="thumbnail"
        )
        await self.create_youtube_subscription(channel_id=channel.id, email=user.email)
        category = await self.create_youtube_video_category(id=1, name="category")
        other_category = await self.create_youtube_video_category(
            id=2, name="other category"
        )
        video_in_category = await self.create_youtube_video(
            id="1",
            title="title_1",
            thumbnail="thumbnail",
            channel_id=channel.id,
            category_id=category.id,
            description="1",
        )
        await self.create_youtube_video(
            id="2",
            title="title_2",
            thumbnail="thumbnail",
            channel_id=channel.id,
            category_id=other_category.id,
            description="2",
        )
        response = await self.client.get(
            f"{VIDEOS_URL}/1/5", params={"video_categories": str(category.id)}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "totalPages": 1,
                "videos": [
                    {
                        "id": video_in_category.id,
                        "title": video_in_category.title,
                        "thumbnail": video_in_category.thumbnail,
                        "categoryId": category.id,
                        "categoryName": category.name,
                        "description": video_in_category.description,
                        "publishedAt": video_in_category.published_at.replace(
                            tzinfo=settings.timezone
                        ).isoformat(),
                        "channelId": channel.id,
                        "channelTitle": channel.title,
                        "channelThumbnail": channel.thumbnail,
                        "liked": None,
                        "queued": None,
                        "watched": None,
                    }
                ],
            },
        )

    async def test_get_videos_with_queued_only(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        channel = await self.create_youtube_channel(
            id="1", title="channel", thumbnail="thumbnail"
        )
        category = await self.create_youtube_video_category(id=1, name="category")
        queued_video = await self.create_youtube_video(
            id="1",
            title="title_1",
            thumbnail="thumbnail",
            channel_id=channel.id,
            category_id=category.id,
            description="1",
        )
        await self.create_youtube_video(
            id="2",
            title="title_2",
            thumbnail="thumbnail",
            channel_id=channel.id,
            category_id=category.id,
            description="2",
        )
        queue = await self.create_youtube_video_queue(
            email=user.email, video_id=queued_video.id
        )
        response = await self.client.get(
            f"{VIDEOS_URL}/1/5", params={"queued_only": True}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "totalPages": 1,
                "videos": [
                    {
                        "id": queued_video.id,
                        "title": queued_video.title,
                        "thumbnail": queued_video.thumbnail,
                        "categoryId": category.id,
                        "categoryName": category.name,
                        "description": queued_video.description,
                        "publishedAt": queued_video.published_at.replace(
                            tzinfo=settings.timezone
                        ).isoformat(),
                        "channelId": channel.id,
                        "channelTitle": channel.title,
                        "channelThumbnail": channel.thumbnail,
                        "liked": None,
                        "queued": queue.created_at.replace(
                            tzinfo=settings.timezone
                        ).isoformat(),
                        "watched": None,
                    }
                ],
            },
        )

    async def test_get_videos_with_queued_only_in_ascending_order_by_created_date(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        channel = await self.create_youtube_channel(
            id="1", title="channel", thumbnail="thumbnail"
        )
        category = await self.create_youtube_video_category(id=1, name="category")
        videos = [
            await self.create_youtube_video(
                id=str(i),
                title=f"title_{i}",
                thumbnail="thumbnail",
                channel_id=channel.id,
                category_id=category.id,
                description=str(i),
            )
            for i in range(5)
        ]
        queues = [
            await self.create_youtube_video_queue(email=user.email, video_id=video.id)
            for video in videos
        ]
        queues.sort(key=lambda queue: queue.created_at)
        videos = list(
            map(
                lambda queue: next(
                    filter(lambda video: video.id == queue.video_id, videos)
                ),
                queues,
            )
        )
        response = await self.client.get(
            f"{VIDEOS_URL}/1/5", params={"queued_only": True}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "totalPages": 1,
                "videos": list(
                    map(
                        lambda i: {
                            "id": videos[i].id,
                            "title": videos[i].title,
                            "thumbnail": videos[i].thumbnail,
                            "categoryId": category.id,
                            "categoryName": category.name,
                            "description": videos[i].description,
                            "publishedAt": videos[i]
                            .published_at.replace(tzinfo=settings.timezone)
                            .isoformat(),
                            "channelId": channel.id,
                            "channelTitle": channel.title,
                            "channelThumbnail": channel.thumbnail,
                            "liked": None,
                            "queued": queues[i]
                            .created_at.replace(tzinfo=settings.timezone)
                            .isoformat(),
                            "watched": None,
                        },
                        range(len(videos)),
                    )
                ),
            },
        )

    async def test_get_videos_with_liked_only(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        other_user = await self.create_user(
            email="other@gmail.com", password="password"
        )
        channel = await self.create_youtube_channel(
            id="1", title="channel", thumbnail="thumbnail"
        )
        category = await self.create_youtube_video_category(id=1, name="category")
        liked_video = await self.create_youtube_video(
            id="1",
            title="title_1",
            thumbnail="thumbnail",
            channel_id=channel.id,
            category_id=category.id,
            description="1",
        )
        other_liked_video = await self.create_youtube_video(
            id="2",
            title="title_2",
            thumbnail="thumbnail",
            channel_id=channel.id,
            category_id=category.id,
            description="2",
        )
        like = await self.create_youtube_video_like(
            email=user.email, video_id=liked_video.id
        )
        await self.create_youtube_video_like(
            email=other_user.email, video_id=other_liked_video.id
        )
        response = await self.client.get(
            f"{VIDEOS_URL}/1/5", params={"liked_only": True}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "totalPages": 1,
                "videos": [
                    {
                        "id": liked_video.id,
                        "title": liked_video.title,
                        "thumbnail": liked_video.thumbnail,
                        "categoryId": category.id,
                        "categoryName": category.name,
                        "description": liked_video.description,
                        "publishedAt": liked_video.published_at.replace(
                            tzinfo=settings.timezone
                        ).isoformat(),
                        "channelId": channel.id,
                        "channelTitle": channel.title,
                        "channelThumbnail": channel.thumbnail,
                        "liked": like.created_at.replace(
                            tzinfo=settings.timezone
                        ).isoformat(),
                        "queued": None,
                        "watched": None,
                    }
                ],
            },
        )

    async def test_get_videos_with_liked_only_in_descending_order_by_created_date(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        channel = await self.create_youtube_channel(
            id="1", title="channel", thumbnail="thumbnail"
        )
        category = await self.create_youtube_video_category(id=1, name="category")
        videos = [
            await self.create_youtube_video(
                id=str(i),
                title=f"title_{i}",
                thumbnail="thumbnail",
                channel_id=channel.id,
                category_id=category.id,
                description=str(i),
            )
            for i in range(5)
        ]
        likes = [
            await self.create_youtube_video_like(email=user.email, video_id=video.id)
            for video in videos
        ]
        likes.sort(key=lambda like: like.created_at, reverse=True)
        videos = list(
            map(
                lambda like: next(
                    filter(lambda video: video.id == like.video_id, videos), videos
                ),
                likes,
            )
        )
        response = await self.client.get(
            f"{VIDEOS_URL}/1/5", params={"liked_only": True}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "totalPages": 1,
                "videos": list(
                    map(
                        lambda i: {
                            "id": videos[i].id,
                            "title": videos[i].title,
                            "thumbnail": videos[i].thumbnail,
                            "categoryId": category.id,
                            "categoryName": category.name,
                            "description": videos[i].description,
                            "publishedAt": videos[i]
                            .published_at.replace(tzinfo=settings.timezone)
                            .isoformat(),
                            "channelId": channel.id,
                            "channelTitle": channel.title,
                            "channelThumbnail": channel.thumbnail,
                            "liked": likes[i]
                            .created_at.replace(tzinfo=settings.timezone)
                            .isoformat(),
                            "queued": None,
                            "watched": None,
                        },
                        range(len(videos)),
                    )
                ),
            },
        )


class GetVideosQueueTestCase(YoutubeBaseTest):
    async def test_get_video_queue_with_empty_queue(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.get(VIDEOS_QUEUE_URL, params={"index": 1})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    async def test_get_video_queue_with_single_video(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        channel = await self.create_youtube_channel(
            id="1", title="channel", thumbnail="thumbnail"
        )
        category = await self.create_youtube_video_category(id=1, name="category")
        video = await self.create_youtube_video(
            id="1",
            title="title",
            thumbnail="thumbnail",
            channel_id=channel.id,
            category_id=category.id,
            description="1",
        )
        video_queue = await self.create_youtube_video_queue(
            email=user.email, video_id=video.id
        )
        response = await self.client.get(VIDEOS_QUEUE_URL, params={"index": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "currentVideo": {
                    "id": video.id,
                    "title": video.title,
                    "thumbnail": video.thumbnail,
                    "categoryId": category.id,
                    "categoryName": category.name,
                    "description": video.description,
                    "publishedAt": video.published_at.replace(
                        tzinfo=settings.timezone
                    ).isoformat(),
                    "channelId": channel.id,
                    "channelTitle": channel.title,
                    "channelThumbnail": channel.thumbnail,
                    "liked": None,
                    "queued": video_queue.created_at.replace(
                        tzinfo=settings.timezone
                    ).isoformat(),
                    "watched": None,
                },
                "prev": False,
                "next": False,
            },
        )

    async def test_get_video_queue_with_next_video(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        channel = await self.create_youtube_channel(
            id="1", title="channel", thumbnail="thumbnail"
        )
        category = await self.create_youtube_video_category(id=1, name="category")
        video = await self.create_youtube_video(
            id="1",
            title="title",
            thumbnail="thumbnail",
            channel_id=channel.id,
            category_id=category.id,
            description="1",
        )
        next_video = await self.create_youtube_video(
            id="2",
            title="title",
            thumbnail="thumbnail",
            channel_id=channel.id,
            category_id=category.id,
            description="2",
        )
        video_queue = await self.create_youtube_video_queue(
            email=user.email, video_id=video.id
        )
        await self.create_youtube_video_queue(email=user.email, video_id=next_video.id)
        response = await self.client.get(VIDEOS_QUEUE_URL, params={"index": 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "currentVideo": {
                    "id": video.id,
                    "title": video.title,
                    "thumbnail": video.thumbnail,
                    "categoryId": category.id,
                    "categoryName": category.name,
                    "description": video.description,
                    "publishedAt": video.published_at.replace(
                        tzinfo=settings.timezone
                    ).isoformat(),
                    "channelId": channel.id,
                    "channelTitle": channel.title,
                    "channelThumbnail": channel.thumbnail,
                    "liked": None,
                    "queued": video_queue.created_at.replace(
                        tzinfo=settings.timezone
                    ).isoformat(),
                    "watched": None,
                },
                "prev": False,
                "next": True,
            },
        )

    async def test_get_video_queue_with_prev_video(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        channel = await self.create_youtube_channel(
            id="1", title="channel", thumbnail="thumbnail"
        )
        category = await self.create_youtube_video_category(id=1, name="category")
        prev_video = await self.create_youtube_video(
            id="1",
            title="title",
            thumbnail="thumbnail",
            channel_id=channel.id,
            category_id=category.id,
            description="1",
        )
        video = await self.create_youtube_video(
            id="2",
            title="title",
            thumbnail="thumbnail",
            channel_id=channel.id,
            category_id=category.id,
            description="2",
        )
        await self.create_youtube_video_queue(email=user.email, video_id=prev_video.id)
        video_queue = await self.create_youtube_video_queue(
            email=user.email, video_id=video.id
        )
        response = await self.client.get(VIDEOS_QUEUE_URL, params={"index": 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "currentVideo": {
                    "id": video.id,
                    "title": video.title,
                    "thumbnail": video.thumbnail,
                    "categoryId": category.id,
                    "categoryName": category.name,
                    "description": video.description,
                    "publishedAt": video.published_at.replace(
                        tzinfo=settings.timezone
                    ).isoformat(),
                    "channelId": channel.id,
                    "channelTitle": channel.title,
                    "channelThumbnail": channel.thumbnail,
                    "liked": None,
                    "queued": video_queue.created_at.replace(
                        tzinfo=settings.timezone
                    ).isoformat(),
                    "watched": None,
                },
                "prev": True,
                "next": False,
            },
        )

    async def test_get_video_queue_with_prev_and_next_videos(self):
        user = await self.create_and_login_user(
            email="user@gmail.com", password="password"
        )
        channel = await self.create_youtube_channel(
            id="1", title="channel", thumbnail="thumbnail"
        )
        category = await self.create_youtube_video_category(id=1, name="category")
        prev_video = await self.create_youtube_video(
            id="1",
            title="title",
            thumbnail="thumbnail",
            channel_id=channel.id,
            category_id=category.id,
            description="1",
        )
        video = await self.create_youtube_video(
            id="2",
            title="title",
            thumbnail="thumbnail",
            channel_id=channel.id,
            category_id=category.id,
            description="2",
        )
        next_video = await self.create_youtube_video(
            id="3",
            title="title",
            thumbnail="thumbnail",
            channel_id=channel.id,
            category_id=category.id,
            description="3",
        )
        await self.create_youtube_video_queue(email=user.email, video_id=prev_video.id)
        video_queue = await self.create_youtube_video_queue(
            email=user.email, video_id=video.id
        )
        await self.create_youtube_video_queue(email=user.email, video_id=next_video.id)
        response = await self.client.get(VIDEOS_QUEUE_URL, params={"index": 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "currentVideo": {
                    "id": video.id,
                    "title": video.title,
                    "thumbnail": video.thumbnail,
                    "categoryId": category.id,
                    "categoryName": category.name,
                    "description": video.description,
                    "publishedAt": video.published_at.replace(
                        tzinfo=settings.timezone
                    ).isoformat(),
                    "channelId": channel.id,
                    "channelTitle": channel.title,
                    "channelThumbnail": channel.thumbnail,
                    "liked": None,
                    "queued": video_queue.created_at.replace(
                        tzinfo=settings.timezone
                    ).isoformat(),
                    "watched": None,
                },
                "prev": True,
                "next": True,
            },
        )
