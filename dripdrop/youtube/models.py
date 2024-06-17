from datetime import datetime
from sqlalchemy import TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dripdrop.authentication.models import User
from dripdrop.base.models import Base


class YoutubeUserChannel(Base):
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
    user: Mapped[User] = relationship(
        User, back_populates="youtube_channels", uselist=True
    )


class YoutubeChannel(Base):
    __tablename__ = "youtube_channels"

    id: Mapped[str] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    thumbnail: Mapped[str | None] = mapped_column(nullable=True)
    last_videos_updated: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )
    updating: Mapped[bool] = mapped_column(nullable=False, default=False)
    subscriptions: Mapped[list["YoutubeSubscription"]] = relationship(
        "YoutubeSubscription", back_populates="channel"
    )
    videos: Mapped[list["YoutubeVideo"]] = relationship(
        "YoutubeVideo", back_populates="channel"
    )


class YoutubeSubscription(Base):
    __tablename__ = "youtube_subscriptions"

    channel_id: Mapped[str] = mapped_column(
        ForeignKey(
            YoutubeChannel.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_subscriptions_channel_id_fkey",
        ),
        nullable=False,
        primary_key=True,
    )
    email: Mapped[str] = mapped_column(
        ForeignKey(
            User.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_subscriptions_email_fkey",
        ),
        nullable=False,
        primary_key=True,
    )
    user_submitted: Mapped[bool] = mapped_column(nullable=False, default=False)
    deleted_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    user: Mapped[User] = relationship(User, back_populates="youtube_subscriptions")
    channel: Mapped[YoutubeChannel] = relationship(
        YoutubeChannel, back_populates="subscriptions"
    )


class YoutubeNewSubscription(Base):
    __tablename__ = "youtube_new_subscriptions"

    channel_id: Mapped[str] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        ForeignKey(
            User.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_new_subscriptions_email_fkey",
        ),
        nullable=False,
        primary_key=True,
    )


class YoutubeVideoCategory(Base):
    __tablename__ = "youtube_video_categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    videos: Mapped[list["YoutubeVideo"]] = relationship(
        "YoutubeVideo", back_populates="category"
    )


class YoutubeVideo(Base):
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
    description: Mapped[str | None] = mapped_column(nullable=True)
    published_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )
    category: Mapped[YoutubeVideoCategory] = relationship(
        YoutubeVideoCategory, back_populates="videos"
    )
    channel: Mapped[YoutubeChannel] = relationship(
        YoutubeChannel, back_populates="videos"
    )
    likes: Mapped[list["YoutubeVideoLike"]] = relationship(
        "YoutubeVideoLike", back_populates="video"
    )
    queues: Mapped[list["YoutubeVideoQueue"]] = relationship(
        "YoutubeVideoQueue", back_populates="video"
    )
    watches: Mapped[list["YoutubeVideoWatch"]] = relationship(
        "YoutubeVideoWatch", back_populates="video"
    )


class YoutubeVideoLike(Base):
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
    user: Mapped[User] = relationship(User, back_populates="youtube_video_likes")
    video: Mapped[YoutubeVideo] = relationship(YoutubeVideo, back_populates="likes")


class YoutubeVideoQueue(Base):
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
    user: Mapped[User] = relationship(User, back_populates="youtube_video_queues")
    video: Mapped[YoutubeVideo] = relationship(YoutubeVideo, back_populates="queues")


class YoutubeVideoWatch(Base):
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
    user: Mapped[User] = relationship(User, back_populates="youtube_video_watches")
    video: Mapped[YoutubeVideo] = relationship(YoutubeVideo, back_populates="watches")
