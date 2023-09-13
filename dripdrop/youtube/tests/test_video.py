from fastapi import status

from dripdrop.youtube.tests.test_base import YoutubeBaseTest

VIDEO_URL = "/api/youtube/video/{video_id}"
VIDEO_QUEUE_URL = "/api/youtube/video/{video_id}/queue"
VIDEO_LIKE_URL = "/api/youtube/video/{video_id}/like"


class GetVideoTestCase(YoutubeBaseTest):
    async def test_get_video_when_not_logged_in(self):
        response = await self.client.get(
            VIDEO_URL.format(video_id=1), params={"related_videos_length": 1}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    async def test_get_video_with_nonexistent_video(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.get(
            VIDEO_URL.format(video_id=1), params={"related_videos_length": 1}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    async def test_get_video_with_no_related_videos(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        channel = await self.create_youtube_channel(
            id="1", title="channel", thumbnail="thumbnail"
        )
        category = await self.create_youtube_video_category(id=1, name="category")
        other_category = await self.create_youtube_video_category(
            id=2, name="category_2"
        )
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
            title="title_2",
            thumbnail="thumbnail",
            channel_id=channel.id,
            category_id=other_category.id,
            description="2",
        )
        response = await self.client.get(
            VIDEO_URL.format(video_id=1), params={"related_videos_length": 1}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "video": {
                    "id": video.id,
                    "title": video.title,
                    "thumbnail": video.thumbnail,
                    "categoryId": category.id,
                    "categoryName": category.name,
                    "description": video.description,
                    "publishedAt": self.convert_to_time_string(video.published_at),
                    "channelId": channel.id,
                    "channelTitle": channel.title,
                    "channelThumbnail": channel.thumbnail,
                    "liked": None,
                    "queued": None,
                    "watched": None,
                },
                "relatedVideos": [],
            },
        )

    async def test_get_video_with_related_videos_by_common_category(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        channel = await self.create_youtube_channel(
            id="1", title="channel", thumbnail="thumbnail"
        )
        other_channel = await self.create_youtube_channel(
            id="2", title="channel_2", thumbnail="thumbnail"
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
        related_video = await self.create_youtube_video(
            id="2",
            title="title_2",
            thumbnail="thumbnail",
            channel_id=other_channel.id,
            category_id=category.id,
            description="2",
        )
        response = await self.client.get(
            VIDEO_URL.format(video_id=1), params={"related_videos_length": 1}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "video": {
                    "id": video.id,
                    "title": video.title,
                    "thumbnail": video.thumbnail,
                    "categoryId": category.id,
                    "categoryName": category.name,
                    "description": video.description,
                    "publishedAt": self.convert_to_time_string(video.published_at),
                    "channelId": channel.id,
                    "channelTitle": channel.title,
                    "channelThumbnail": channel.thumbnail,
                    "liked": None,
                    "queued": None,
                    "watched": None,
                },
                "relatedVideos": [
                    {
                        "id": related_video.id,
                        "title": related_video.title,
                        "thumbnail": related_video.thumbnail,
                        "categoryId": category.id,
                        "categoryName": category.name,
                        "description": related_video.description,
                        "publishedAt": self.convert_to_time_string(
                            related_video.published_at
                        ),
                        "channelId": other_channel.id,
                        "channelTitle": other_channel.title,
                        "channelThumbnail": other_channel.thumbnail,
                        "liked": None,
                        "queued": None,
                        "watched": None,
                    }
                ],
            },
        )


class AddVideoLikeTestCase(YoutubeBaseTest):
    async def test_add_video_like_when_not_logged_in(self):
        response = await self.client.put(VIDEO_LIKE_URL.format(video_id=1))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    async def test_add_video_like_with_nonexistent_video(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.put(VIDEO_LIKE_URL.format(video_id=1))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    async def test_add_video_like(self):
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
        )
        response = await self.client.put(VIDEO_LIKE_URL.format(video_id=video.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(
            await self.get_youtube_video_like(email=user.email, video_id=video.id)
        )

    async def test_add_video_like_with_the_same_video(self):
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
        )
        await self.create_youtube_video_like(email=user.email, video_id=video.id)
        response = await self.client.put(VIDEO_LIKE_URL.format(video_id=video.id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DeleteVideoLikeTestCase(YoutubeBaseTest):
    async def test_delete_video_like_when_not_logged_in(self):
        response = await self.client.delete(VIDEO_LIKE_URL.format(video_id=1))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    async def test_delete_video_like_with_nonexistent_video_like(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.delete(VIDEO_LIKE_URL.format(video_id=1))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    async def test_delete_video_like(self):
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
        )
        await self.create_youtube_video_like(email=user.email, video_id=video.id)
        response = await self.client.delete(VIDEO_LIKE_URL.format(video_id=video.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(
            await self.get_youtube_video_like(email=user.email, video_id=video.id)
        )


class AddVideoQueueTestCase(YoutubeBaseTest):
    async def test_add_video_queue_when_not_logged_in(self):
        response = await self.client.put(VIDEO_QUEUE_URL.format(video_id=1))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    async def test_add_video_queue_with_nonexistent_video(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.put(VIDEO_QUEUE_URL.format(video_id=1))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    async def test_add_video_queue(self):
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
        response = await self.client.put(VIDEO_QUEUE_URL.format(video_id=1))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(
            await self.get_youtube_video_queue(email=user.email, video_id=video.id)
        )

    async def test_add_video_queue_with_the_same_video(self):
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
        await self.create_youtube_video_queue(email=user.email, video_id=video.id)
        response = await self.client.put(VIDEO_QUEUE_URL.format(video_id=video.id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DeleteVideoQueueTestCase(YoutubeBaseTest):
    async def test_delete_video_queue_when_not_logged_in(self):
        response = await self.client.delete(VIDEO_QUEUE_URL.format(video_id=1))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    async def test_delete_video_queue_with_nonexistent_video_queue(self):
        await self.create_and_login_user(email="user@gmail.com", password="password")
        response = await self.client.delete(VIDEO_QUEUE_URL.format(video_id=1))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    async def test_delete_video_queue(self):
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
        await self.create_youtube_video_queue(email=user.email, video_id=video.id)
        response = await self.client.delete(VIDEO_QUEUE_URL.format(video_id=video.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(
            await self.get_youtube_video_queue(email=user.email, video_id=video.id)
        )
