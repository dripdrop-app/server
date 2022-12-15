from datetime import datetime
from dripdrop.models import ApiBase, OrmBase, get_current_time
from dripdrop.authentication.models import Users
from pydantic import Field
from sqlalchemy import (
    Column,
    String,
    TIMESTAMP,
    ForeignKey,
    Boolean,
    Integer,
)
from sqlalchemy.orm import relationship
from typing import Optional


class GoogleAccounts(OrmBase):
    __tablename__ = "google_accounts"

    email = Column(String, primary_key=True)
    user_email = Column(
        ForeignKey(
            Users.email,
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
    subscriptions_loading = Column(
        Boolean,
        nullable=False,
        server_default="0",
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=get_current_time,
    )
    last_updated = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=get_current_time,
        onupdate=get_current_time,
    )
    user = relationship(
        "Users",
        back_populates="google_account",
        uselist=False,
    )
    subscriptions = relationship(
        "YoutubeSubscriptions",
        back_populates="google_account",
    )
    likes = relationship("YoutubeVideoLikes", back_populates="google_account")
    queues = relationship("YoutubeVideoQueues", back_populates="google_account")
    watches = relationship("YoutubeVideoWatches", back_populates="google_account")


class GoogleAccount(ApiBase):
    email: str
    user_email: str
    access_token: str
    refresh_token: str
    expires: int
    subscriptions_loading: bool
    created_at: datetime
    last_updated: datetime


class YoutubeChannels(OrmBase):
    __tablename__ = "youtube_channels"
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    thumbnail = Column(String, nullable=True)
    upload_playlist_id = Column(String, nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=get_current_time,
    )
    last_updated = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        onupdate=get_current_time,
    )
    subscriptions = relationship("YoutubeSubscriptions", back_populates="channel")
    videos = relationship("YoutubeVideos", back_populates="channel")


class YoutubeChannel(ApiBase):
    id: str
    title: str
    thumbnail: Optional[str] = Field(None)
    upload_playlist_id: Optional[str] = Field(None)
    created_at: datetime
    last_updated: datetime


class YoutubeSubscriptions(OrmBase):
    __tablename__ = "youtube_subscriptions"
    id = Column(String, primary_key=True)
    channel_id = Column(
        ForeignKey(
            YoutubeChannels.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_subscriptions_channel_id_fkey",
        ),
        nullable=False,
    )
    email = Column(
        ForeignKey(
            GoogleAccounts.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_subscriptions_email_fkey",
        ),
        nullable=False,
    )
    published_at = Column(TIMESTAMP(timezone=True), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=get_current_time,
    )
    channel = relationship("YoutubeChannels", back_populates="subscriptions")
    google_account = relationship("GoogleAccounts", back_populates="subscriptions")


class YoutubeSubscription(ApiBase):
    id: str
    channel_id: str
    email: str
    published_at: datetime
    created_at: datetime


class YoutubeVideoCategories(OrmBase):
    __tablename__ = "youtube_video_categories"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=get_current_time,
    )
    videos = relationship("YoutubeVideos", back_populates="category")


class YoutubeVideoCategory(ApiBase):
    id: int
    name: str
    created_at: datetime


class YoutubeVideos(OrmBase):
    __tablename__ = "youtube_videos"
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    thumbnail = Column(String, nullable=False)
    channel_id = Column(
        ForeignKey(
            YoutubeChannels.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_videos_channel_id_fkey",
        ),
        nullable=False,
    )
    category_id = Column(
        ForeignKey(
            YoutubeVideoCategories.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_videos_category_id_fkey",
        ),
        nullable=False,
    )
    published_at = Column(TIMESTAMP(timezone=True), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=get_current_time,
    )
    channel = relationship("YoutubeChannels", back_populates="videos")
    category = relationship("YoutubeVideoCategories", back_populates="videos")
    likes = relationship("YoutubeVideoLikes", back_populates="video")
    queues = relationship("YoutubeVideoQueues", back_populates="video")
    watches = relationship("YoutubeVideoWatches", back_populates="video")


class YoutubeVideo(ApiBase):
    id: str
    title: str
    thumbnail: str
    channel_id: str
    category_id: int
    published_at: datetime
    created_at: datetime


class YoutubeVideoLikes(OrmBase):
    __tablename__ = "youtube_video_likes"
    email = Column(
        ForeignKey(
            GoogleAccounts.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_video_likes_email_fkey",
        ),
        primary_key=True,
        nullable=False,
    )
    video_id = Column(
        ForeignKey(
            YoutubeVideos.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_video_likes_video_id_fkey",
        ),
        primary_key=True,
        nullable=False,
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=get_current_time,
    )
    google_account = relationship("GoogleAccounts", back_populates="likes")
    video = relationship("YoutubeVideos", back_populates="likes")


class YoutubeVideoLike(ApiBase):
    email: str
    video_id: str
    created_at: datetime


class YoutubeVideoQueues(OrmBase):
    __tablename__ = "youtube_video_queues"
    email = Column(
        ForeignKey(
            GoogleAccounts.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_video_queues_email_fkey",
        ),
        primary_key=True,
        nullable=False,
    )
    video_id = Column(
        ForeignKey(
            YoutubeVideos.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_video_queues_video_id_fkey",
        ),
        primary_key=True,
        nullable=False,
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=get_current_time,
    )
    google_account = relationship("GoogleAccounts", back_populates="queues")
    video = relationship("YoutubeVideos", back_populates="queues")


class YoutubeVideoQueue(ApiBase):
    email: str
    video_id: str
    created_at: datetime


class YoutubeVideoWatches(OrmBase):
    __tablename__ = "youtube_video_watches"
    email = Column(
        ForeignKey(
            GoogleAccounts.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_video_watches_email_fkey",
        ),
        primary_key=True,
        nullable=False,
    )
    video_id = Column(
        ForeignKey(
            YoutubeVideos.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_video_watches_video_id_fkey",
        ),
        primary_key=True,
        nullable=False,
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=get_current_time,
    )
    google_account = relationship("GoogleAccounts", back_populates="watches")
    video = relationship("YoutubeVideos", back_populates="watches")


class YoutubeVideoWatch(ApiBase):
    email: str
    video_id: str
    created_at: datetime
