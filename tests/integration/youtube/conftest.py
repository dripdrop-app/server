import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from dripdrop.apps.youtube.models import (
    GoogleAccount,
    YoutubeChannel,
    YoutubeSubscription,
    YoutubeVideo,
    YoutubeVideoCategory,
    YoutubeVideoQueue,
    YoutubeVideoLike,
    YoutubeVideoWatch,
)
from dripdrop.settings import settings


@pytest.fixture
def create_google_account(session: Session):
    def _create_google_account(
        email: str = ...,
        user_email: str = ...,
        access_token: str = ...,
        refresh_token: str = ...,
        expires: int = 1000,
    ):
        google_account = GoogleAccount(
            email=email,
            user_email=user_email,
            access_token=access_token,
            refresh_token=refresh_token,
            expires=expires,
        )
        session.add(google_account)
        session.commit()
        return google_account

    return _create_google_account


@pytest.fixture
def create_channel(session: Session):
    def _create_channel(
        id: str = ...,
        title: str = ...,
        thumbnail: str = ...,
        upload_playlist_id: str = ...,
        last_updated: datetime | None = None,
        last_videos_updated: datetime | None = None,
    ):
        youtube_channel = YoutubeChannel(
            id=id,
            title=title,
            thumbnail=thumbnail,
            upload_playlist_id=upload_playlist_id,
            last_updated=last_updated
            if last_updated
            else datetime.now(tz=settings.timezone),
            last_videos_updated=last_videos_updated
            if last_videos_updated
            else datetime.now(tz=settings.timezone),
        )
        session.add(youtube_channel)
        session.commit()
        return youtube_channel

    return _create_channel


@pytest.fixture
def create_subscription(session: Session):
    def _create_subscription(
        id: str = ...,
        channel_id: str = ...,
        email: str = ...,
        published_at: datetime | None = None,
    ):
        youtube_subscription = YoutubeSubscription(
            id=id,
            channel_id=channel_id,
            email=email,
            published_at=published_at
            if published_at
            else datetime.now(tz=settings.timezone),
        )
        session.add(youtube_subscription)
        session.commit()
        return youtube_subscription

    return _create_subscription


@pytest.fixture
def create_video_category(session: Session):
    def _create_video_category(id: int = ..., name: str = ...):
        youtube_video_category = YoutubeVideoCategory(id=id, name=name)
        session.add(youtube_video_category)
        session.commit()
        return youtube_video_category

    return _create_video_category


@pytest.fixture
def create_video(session: Session):
    def _create_video(
        id: str = ...,
        title: str = ...,
        thumbnail: str = ...,
        channel_id: str = ...,
        category_id: int = ...,
        published_at: datetime | None = None,
    ):
        youtube_video = YoutubeVideo(
            id=id,
            title=title,
            thumbnail=thumbnail,
            channel_id=channel_id,
            category_id=category_id,
            published_at=published_at
            if published_at
            else datetime.now(settings.timezone),
        )
        session.add(youtube_video)
        session.commit()
        return youtube_video

    return _create_video


@pytest.fixture
def create_video_queue(session: Session):
    def _create_video_queue(email: str = ..., video_id: str = ...):
        youtube_video_queue = YoutubeVideoQueue(email=email, video_id=video_id)
        session.add(youtube_video_queue)
        session.commit()
        return youtube_video_queue

    return _create_video_queue


@pytest.fixture
def create_video_like(session: Session):
    def _create_video_like(email: str = ..., video_id: str = ...):
        youtube_video_like = YoutubeVideoLike(email=email, video_id=video_id)
        session.add(youtube_video_like)
        session.commit()
        return youtube_video_like

    return _create_video_like


@pytest.fixture
def create_video_watch(session: Session):
    def _create_video_watch(email: str = ..., video_id: str = ...):
        youtube_video_watch = YoutubeVideoWatch(email=email, video_id=video_id)
        session.add(youtube_video_watch)
        session.commit()
        return youtube_video_watch

    return _create_video_watch
