import dateutil.parser
import traceback
from datetime import datetime, timedelta
from sqlalchemy import select, func, delete

from dripdrop.database import Session
from dripdrop.logging import logger
from dripdrop.services.google_api import google_api_service
from dripdrop.settings import settings
from dripdrop.rq import queue
from dripdrop.utils import worker_task, exception_handler

from .models import (
    GoogleAccount,
    YoutubeChannel,
    YoutubeSubscription,
    YoutubeVideo,
    YoutubeVideoCategory,
)
from .utils import update_google_access_token


class YoutubeTasker:
    def enqueue(self, *args, **kwargs):
        queue.enqueue(*args, **kwargs, at_front=True)

    @exception_handler
    def add_update_youtube_subscription(
        self,
        google_email: str = ...,
        subscription: dict = ...,
        session: Session = ...,
    ):
        subscription_id = subscription["id"]
        subscription_channel_id = subscription["snippet"]["resourceId"]["channelId"]
        subscription_published_at = dateutil.parser.parse(
            subscription["snippet"]["publishedAt"]
        )
        query = select(YoutubeSubscription).where(
            YoutubeSubscription.id == subscription_id,
            YoutubeSubscription.email == google_email,
        )
        results = session.scalars(query)
        subscription: YoutubeSubscription | None = results.first()
        if subscription:
            subscription.published_at = subscription_published_at
        else:
            session.add(
                YoutubeSubscription(
                    id=subscription_id,
                    channel_id=subscription_channel_id,
                    email=google_email,
                    published_at=subscription_published_at,
                )
            )
        session.commit()

    @exception_handler
    def add_update_youtube_channel(self, channel: dict = ..., session: Session = ...):
        channel_id = channel["id"]
        channel_title = channel["snippet"]["title"]
        channel_upload_playlist_id = channel["contentDetails"]["relatedPlaylists"][
            "uploads"
        ]
        channel_thumbnail = channel["snippet"]["thumbnails"]["high"]["url"]
        query = select(YoutubeChannel).where(YoutubeChannel.id == channel_id)
        results = session.scalars(query)
        channel: YoutubeChannel | None = results.first()
        if channel:
            channel.title = channel_title
            channel.thumbnail = channel_thumbnail
            channel.upload_playlist_id = channel_upload_playlist_id
        else:
            session.add(
                YoutubeChannel(
                    id=channel_id,
                    title=channel_title,
                    thumbnail=channel_thumbnail,
                    upload_playlist_id=channel_upload_playlist_id,
                    last_videos_updated=datetime.now(tz=settings.timezone)
                    - timedelta(days=32),
                )
            )
        session.commit()

    @exception_handler
    def add_update_youtube_video(self, video: dict = ..., session: Session = ...):
        video_id = video["id"]
        video_title = video["snippet"]["title"]
        video_thumbnail = video["snippet"]["thumbnails"]["high"]["url"]
        video_channel_id = video["snippet"]["channelId"]
        video_published_at = dateutil.parser.parse(video["snippet"]["publishedAt"])
        video_category_id = int(video["snippet"]["categoryId"])
        query = select(YoutubeVideo).where(YoutubeVideo.id == video_id)
        results = session.scalars(query)
        video: YoutubeVideo = results.first()
        if video:
            video.title = video_title
            video.thumbnail = video_thumbnail
            video.published_at = video_published_at
            video.category_id = video_category_id
        else:
            session.add(
                YoutubeVideo(
                    id=video_id,
                    title=video_title,
                    thumbnail=video_thumbnail,
                    channel_id=video_channel_id,
                    published_at=video_published_at,
                    category_id=video_category_id,
                )
            )
        session.commit()

    @worker_task
    def update_channels(self, channel_ids: list[int] = ..., session: Session = ...):
        channels_info = google_api_service.get_channels_info(channel_ids=channel_ids)
        for channel_info in channels_info:
            self.add_update_youtube_channel(channel=channel_info, session=session)

    @exception_handler
    def add_update_youtube_video_category(
        self, category: dict = ..., session: Session = ...
    ):
        category_id = int(category["id"])
        category_title = category["snippet"]["title"]
        logger.exception(traceback.format_exc())
        query = select(YoutubeVideoCategory).where(
            YoutubeVideoCategory.id == category_id
        )
        results = session.scalars(query)
        category: YoutubeVideoCategory | None = results.first()
        if category:
            category.name = category_title
        else:
            session.add(YoutubeVideoCategory(id=category_id, name=category_title))
        session.commit()

    @worker_task
    def update_youtube_video_categories(self, cron: bool = ..., session: Session = ...):
        if not cron:
            query = select(func.count(YoutubeVideoCategory.id))
            count = session.scalar(query)
            if count > 0:
                return
        video_categories = google_api_service.get_video_categories()
        for category in video_categories:
            self.add_update_youtube_video_category(category=category, session=session)

    @worker_task
    def update_user_youtube_subscriptions_job(
        self, user_email: str = ..., session: Session = ...
    ):
        query = select(GoogleAccount).where(GoogleAccount.user_email == user_email)
        results = session.scalars(query)
        account: GoogleAccount | None = results.first()
        if not account:
            return
        session.commit()
        update_google_access_token(google_email=account.email, session=session)
        session.refresh(account)
        if not account.access_token:
            return

        for subscriptions in google_api_service.get_user_subscriptions(
            access_token=account.access_token
        ):
            subscription_channel_ids = [
                subscription["snippet"]["resourceId"]["channelId"]
                for subscription in subscriptions
            ]
            query = select(YoutubeChannel).where(
                YoutubeChannel.id.in_(subscription_channel_ids)
            )
            results = session.scalars(query)
            channels: list[YoutubeChannel] = results.all()
            channel_ids = [channel.id for channel in channels]
            new_channel_ids = list(
                filter(
                    lambda channel_id: channel_id not in channel_ids,
                    subscription_channel_ids,
                )
            )
            if len(new_channel_ids) > 0:
                channels_info = google_api_service.get_channels_info(
                    channel_ids=new_channel_ids
                )
                for channel_info in channels_info:
                    self.add_update_youtube_channel(
                        channel=channel_info, session=session
                    )
            for subscription in subscriptions:
                self.add_update_youtube_subscription(
                    google_email=account.email,
                    subscription=subscription,
                    session=session,
                )

    @worker_task
    def add_new_channel_videos_job(self, channel_id: str = ..., session: Session = ...):
        query = select(YoutubeChannel).where(YoutubeChannel.id == channel_id)
        results = session.scalars(query)
        channel: YoutubeChannel | None = results.first()
        for uploaded_playlist_videos in google_api_service.get_playlist_videos(
            playlist_id=channel.upload_playlist_id
        ):
            new_videos = []
            video_ids = []
            for uploaded_video in uploaded_playlist_videos:
                video_published_at = dateutil.parser.parse(
                    uploaded_video["contentDetails"]["videoPublishedAt"]
                )
                uploaded_video["contentDetails"][
                    "videoPublishedAt"
                ] = video_published_at
                video_ids.append(uploaded_video["contentDetails"]["videoId"])
                if video_published_at > channel.last_videos_updated:
                    new_videos.append(uploaded_video)
            videos_info = google_api_service.get_videos_info(video_ids=video_ids)
            for video_info in videos_info:
                self.add_update_youtube_video(video=video_info, session=session)
            if len(new_videos) < len(uploaded_playlist_videos):
                break
        channel.last_videos_updated = datetime.now(tz=settings.timezone)
        session.commit()

    @worker_task
    def update_subscribed_channels_videos(self, session: Session = ...):
        query = select([YoutubeSubscription.channel_id.distinct()])
        stream = session.scalars(query)
        for subscription in stream.yield_per(10):
            self.enqueue(
                self.add_new_channel_videos_job,
                kwargs={"channel_id": subscription.channel_id},
            )

    @worker_task
    def update_subscribed_channels_meta(self, session: Session = ...):
        CHANNEL_NUM = 50
        page = 0
        while True:
            query = select([YoutubeSubscription.channel_id.distinct()]).offset(
                page * CHANNEL_NUM
            )
            results = session.scalars(query)
            subscriptions: list[YoutubeSubscription] = results.fetchmany(CHANNEL_NUM)
            if len(subscriptions) == 0:
                break
            channel_ids = [subscription.channel_id for subscription in subscriptions]
            self.enqueue(self.update_channels, kwargs={"channel_ids": channel_ids})
            page += 1

    @worker_task
    def update_subscriptions(self, session: Session = ...):
        query = select(GoogleAccount)
        stream = session.scalars(query)
        for account in stream.yield_per(10):
            self.enqueue(
                self.update_user_youtube_subscriptions_job,
                kwargs={"user_email": account.user_email},
            )

    @worker_task
    def delete_channel(self, channel_id: str = ..., session: Session = ...):
        query = select(YoutubeChannel).where(YoutubeChannel.id == channel_id)
        results = session.scalars(query)
        channel: YoutubeChannel | None = results.first()
        if not channel:
            raise Exception(f"Channel ({channel_id}) not found")
        query = delete(YoutubeSubscription).where(
            YoutubeSubscription.channel_id == channel.id
        )
        session.execute(query)
        session.commit()
        session.delete(channel)
        session.commit()

    @worker_task
    def delete_old_channels(self, session: Session = ...):
        limit = datetime.now(tz=settings.timezone) - timedelta(days=7)
        query = select(YoutubeChannel).where(YoutubeChannel.last_videos_updated < limit)
        stream = session.scalars(query)
        for channel in stream.yield_per(10):
            self.enqueue(self.delete_channel, kwargs={"channel_id": channel.id})


youtube_tasker = YoutubeTasker()
