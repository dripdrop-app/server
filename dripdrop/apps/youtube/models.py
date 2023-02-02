from sqlalchemy import (
    Column,
    String,
    TIMESTAMP,
    ForeignKey,
    Integer,
)

from dripdrop.apps.authentication.models import User
from dripdrop.models.base import Base, ModelBaseMixin


class GoogleAccount(ModelBaseMixin, Base):
    __tablename__ = "google_accounts"
    email = Column(String, primary_key=True)
    user_email = Column(
        ForeignKey(
            User.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="google_accounts_user_email_fkey",
        ),
        nullable=False,
        unique=True,
    )
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    expires = Column(Integer, nullable=False)


class YoutubeChannel(ModelBaseMixin, Base):
    __tablename__ = "youtube_channels"
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    thumbnail = Column(String, nullable=True)
    upload_playlist_id = Column(String, nullable=True)
    last_videos_updated = Column(TIMESTAMP(timezone=True), nullable=False)


class YoutubeSubscription(ModelBaseMixin, Base):
    __tablename__ = "youtube_subscriptions"
    id = Column(String, primary_key=True)
    channel_id = Column(
        ForeignKey(
            YoutubeChannel.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_subscriptions_channel_id_fkey",
        ),
        nullable=False,
    )
    email = Column(
        ForeignKey(
            GoogleAccount.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_subscriptions_email_fkey",
        ),
        nullable=False,
    )
    published_at = Column(TIMESTAMP(timezone=True), nullable=False)


class YoutubeVideoCategory(ModelBaseMixin, Base):
    __tablename__ = "youtube_video_categories"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class YoutubeVideo(ModelBaseMixin, Base):
    __tablename__ = "youtube_videos"
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    thumbnail = Column(String, nullable=False)
    channel_id = Column(
        ForeignKey(
            YoutubeChannel.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_videos_channel_id_fkey",
        ),
        nullable=False,
    )
    category_id = Column(
        ForeignKey(
            YoutubeVideoCategory.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_videos_category_id_fkey",
        ),
        nullable=False,
    )
    published_at = Column(TIMESTAMP(timezone=True), nullable=False)


class YoutubeVideoLike(ModelBaseMixin, Base):
    __tablename__ = "youtube_video_likes"
    email = Column(
        ForeignKey(
            GoogleAccount.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_video_likes_email_fkey",
        ),
        primary_key=True,
        nullable=False,
    )
    video_id = Column(
        ForeignKey(
            YoutubeVideo.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_video_likes_video_id_fkey",
        ),
        primary_key=True,
        nullable=False,
    )


class YoutubeVideoQueue(ModelBaseMixin, Base):
    __tablename__ = "youtube_video_queues"
    email = Column(
        ForeignKey(
            GoogleAccount.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_video_queues_email_fkey",
        ),
        primary_key=True,
        nullable=False,
    )
    video_id = Column(
        ForeignKey(
            YoutubeVideo.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_video_queues_video_id_fkey",
        ),
        primary_key=True,
        nullable=False,
    )


class YoutubeVideoWatch(ModelBaseMixin, Base):
    __tablename__ = "youtube_video_watches"
    email = Column(
        ForeignKey(
            GoogleAccount.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_video_watches_email_fkey",
        ),
        primary_key=True,
        nullable=False,
    )
    video_id = Column(
        ForeignKey(
            YoutubeVideo.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_video_watches_video_id_fkey",
        ),
        primary_key=True,
        nullable=False,
    )
