import pytest
from datetime import datetime, timezone
from sqlalchemy import insert
from sqlalchemy.engine import Connection

from dripdrop.apps.youtube.models import (
    GoogleAccount,
    YoutubeChannel,
    YoutubeSubscription,
)


@pytest.fixture
def create_google_account(db: Connection):
    def _create_google_account(
        email: str = ...,
        user_email: str = ...,
        access_token: str = ...,
        refresh_token: str = ...,
        expires: int = 1000,
    ):
        db.execute(
            insert(GoogleAccount).values(
                email=email,
                user_email=user_email,
                access_token=access_token,
                refresh_token=refresh_token,
                expires=expires,
            )
        )

    return _create_google_account


@pytest.fixture(autouse=True)
def create_default_user(create_and_login_user, test_email, test_password, request):
    if "noauth" in request.keywords:
        return
    create_and_login_user(test_email, test_password, admin=False)


@pytest.fixture(autouse=True)
def create_google_default_user(create_google_account, test_email, request):
    if "nogoogleauth" in request.keywords:
        return
    create_google_account(
        email=test_email,
        user_email=test_email,
        access_token="test_access_token",
        refresh_token="test_refresh_token",
    )


@pytest.fixture
def create_channel(db: Connection):
    def _create_channel(
        id: str = ...,
        title: str = ...,
        thumbnail: str = ...,
        upload_playlist_id: str = ...,
        last_updated: datetime | None = datetime.now(timezone.utc),
    ):
        db.execute(
            insert(YoutubeChannel).values(
                id=id,
                title=title,
                thumbnail=thumbnail,
                upload_playlist_id=upload_playlist_id,
                last_updated=last_updated,
            )
        )

    return _create_channel


@pytest.fixture
def create_subscription(db: Connection):
    def _create_subscription(
        id: str = ...,
        channel_id: str = ...,
        email: str = ...,
        published_at: datetime | None = datetime.now(timezone.utc),
    ):
        db.execute(
            insert(YoutubeSubscription).values(
                id=id, channel_id=channel_id, email=email, published_at=published_at
            )
        )

    return _create_subscription
