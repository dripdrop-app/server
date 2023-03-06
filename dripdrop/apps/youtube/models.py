from datetime import datetime
from sqlalchemy import TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from dripdrop.apps.authentication.models import User
from dripdrop.models.base import Base, ModelBaseMixin


class YoutubeUserChannel(ModelBaseMixin, Base):
    __tablename__ = "youtube_user_channels"

    id: Mapped[str] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        ForeignKey(
            User.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_user_channels_email_fkey",
        ),
        unique=True,
    )


class YoutubeChannel(ModelBaseMixin, Base):
    __tablename__ = "youtube_channels"

    id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    thumbnail: Mapped[str | None] = mapped_column(nullable=True)
    last_videos_updated: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )


class YoutubeSubscription(ModelBaseMixin, Base):
    __tablename__ = "youtube_subscriptions"

    id: Mapped[str] = mapped_column(primary_key=True)
    channel_id: Mapped[str] = mapped_column(
        ForeignKey(
            YoutubeChannel.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_subscriptions_channel_id_fkey",
        ),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        ForeignKey(
            User.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_subscriptions_email_fkey",
        ),
        nullable=False,
    )
    published_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )
    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )


class YoutubeNewSubscription(ModelBaseMixin, Base):
    __tablename__ = "youtube_new_subscriptions"

    id: Mapped[str] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        ForeignKey(
            User.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_new_subscriptions_email_fkey",
        ),
        nullable=False,
    )


class YoutubeVideoCategory(ModelBaseMixin, Base):
    __tablename__ = "youtube_video_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)


class YoutubeVideo(ModelBaseMixin, Base):
    __tablename__ = "youtube_videos"

    id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    thumbnail: Mapped[str] = mapped_column(nullable=False)
    channel_id: Mapped[str] = mapped_column(
        ForeignKey(
            YoutubeChannel.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_videos_channel_id_fkey",
        ),
        nullable=False,
    )
    category_id: Mapped[int] = mapped_column(
        ForeignKey(
            YoutubeVideoCategory.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_videos_category_id_fkey",
        ),
        nullable=False,
    )
    published_at: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )


class YoutubeVideoLike(ModelBaseMixin, Base):
    __tablename__ = "youtube_video_likes"

    email: Mapped[str] = mapped_column(
        ForeignKey(
            User.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_video_likes_email_fkey",
        ),
        primary_key=True,
        nullable=False,
    )
    video_id: Mapped[str] = mapped_column(
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

    email: Mapped[str] = mapped_column(
        ForeignKey(
            User.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_video_queues_email_fkey",
        ),
        primary_key=True,
        nullable=False,
    )
    video_id: Mapped[str] = mapped_column(
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

    email: Mapped[str] = mapped_column(
        ForeignKey(
            User.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_video_watches_email_fkey",
        ),
        primary_key=True,
        nullable=False,
    )
    video_id: Mapped[str] = mapped_column(
        ForeignKey(
            YoutubeVideo.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_video_watches_video_id_fkey",
        ),
        primary_key=True,
        nullable=False,
    )
