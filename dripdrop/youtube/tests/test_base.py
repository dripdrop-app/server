from datetime import datetime
from sqlalchemy import select

from dripdrop.base.test import BaseTest
from dripdrop.settings import settings
from dripdrop.youtube.models import (
    YoutubeUserChannel,
    YoutubeChannel,
    YoutubeSubscription,
    YoutubeVideo,
    YoutubeVideoCategory,
    YoutubeVideoLike,
    YoutubeVideoQueue,
    YoutubeVideoWatch,
)


class YoutubeBaseTest(BaseTest):
    async def update_user_youtube_channel(
        self, id: str, email: str, modified_at: datetime | None = None
    ):
        user_youtube_channel = YoutubeUserChannel(
            id=id, email=email, modified_at=modified_at
        )
        self.session.add(user_youtube_channel)
        await self.session.commit()
        return user_youtube_channel

    async def get_user_youtube_channel(self, email: str):
        query = select(YoutubeUserChannel).where(YoutubeUserChannel.email == email)
        results = await self.session.scalars(query)
        user_youtube_channel = results.first()
        return user_youtube_channel

    async def create_youtube_channel(
        self,
        id: str,
        title: str,
        thumbnail: str,
        modified_at: datetime | None = None,
        last_videos_updated: datetime | None = None,
    ):
        youtube_channel = YoutubeChannel(
            id=id,
            title=title,
            thumbnail=thumbnail,
            last_videos_updated=last_videos_updated
            if last_videos_updated
            else datetime.now(tz=settings.timezone),
            modified_at=modified_at
            if modified_at
            else datetime.now(tz=settings.timezone),
        )
        self.session.add(youtube_channel)
        await self.session.commit()
        return youtube_channel

    async def create_youtube_subscription(
        self,
        channel_id: str,
        email: str,
        user_submitted: str | None = None,
        deleted_at: datetime | None = None,
    ):
        youtube_subscription = YoutubeSubscription(
            channel_id=channel_id,
            email=email,
            user_submitted=user_submitted,
            deleted_at=deleted_at,
        )
        self.session.add(youtube_subscription)
        await self.session.commit()
        return youtube_subscription

    async def create_youtube_video_category(self, id: int, name: str):
        youtube_video_category = YoutubeVideoCategory(id=id, name=name)
        self.session.add(youtube_video_category)
        await self.session.commit()
        return youtube_video_category

    async def create_youtube_video(
        self,
        id: str,
        title: str,
        thumbnail: str,
        channel_id: str,
        category_id: int,
        description: str | None = None,
        published_at: datetime | None = None,
    ):
        youtube_video = YoutubeVideo(
            id=id,
            title=title,
            thumbnail=thumbnail,
            channel_id=channel_id,
            category_id=category_id,
            description=description,
            published_at=published_at
            if published_at
            else datetime.now(settings.timezone),
        )
        self.session.add(youtube_video)
        await self.session.commit()
        return youtube_video

    async def create_youtube_video_queue(self, email: str, video_id: str):
        youtube_video_queue = YoutubeVideoQueue(email=email, video_id=video_id)
        self.session.add(youtube_video_queue)
        await self.session.commit()
        return youtube_video_queue

    async def get_youtube_video_queue(self, email: str, video_id: str):
        query = select(YoutubeVideoQueue).where(
            YoutubeVideoQueue.email == email, YoutubeVideoQueue.video_id == video_id
        )
        results = await self.session.scalars(query)
        youtube_video_queue = results.first()
        return youtube_video_queue

    async def create_youtube_video_like(self, email: str, video_id: str):
        youtube_video_like = YoutubeVideoLike(email=email, video_id=video_id)
        self.session.add(youtube_video_like)
        await self.session.commit()
        return youtube_video_like

    async def get_youtube_video_like(self, email: str, video_id: str):
        query = select(YoutubeVideoLike).where(
            YoutubeVideoLike.email == email, YoutubeVideoLike.video_id == video_id
        )
        results = await self.session.scalars(query)
        youtube_video_queue = results.first()
        return youtube_video_queue

    async def create_youtube_video_watch(self, email: str, video_id: str):
        youtube_video_watch = YoutubeVideoWatch(email=email, video_id=video_id)
        self.session.add(youtube_video_watch)
        await self.session.commit()
        return youtube_video_watch

    async def get_youtube_video_watch(self, email: str, video_id: str):
        query = select(YoutubeVideoWatch).where(
            YoutubeVideoWatch.email == email, YoutubeVideoWatch.video_id == video_id
        )
        results = await self.session.scalars(query)
        youtube_video_queue = results.first()
        return youtube_video_queue
