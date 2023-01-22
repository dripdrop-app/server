import pytest
from datetime import datetime
from sqlalchemy.orm import Session

from dripdrop.apps.youtube.models import (
    GoogleAccount,
    YoutubeChannel,
    YoutubeSubscription,
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
        last_updated: datetime | None = datetime.now(tz=settings.timezone),
    ):
        youtube_channel = YoutubeChannel(
            id=id,
            title=title,
            thumbnail=thumbnail,
            upload_playlist_id=upload_playlist_id,
            last_updated=last_updated,
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
        published_at: datetime | None = datetime.now(tz=settings.timezone),
    ):
        youtube_subscription = YoutubeSubscription(
            id=id, channel_id=channel_id, email=email, published_at=published_at
        )
        session.add(youtube_subscription)
        session.commit()
        return youtube_subscription

    return _create_subscription
