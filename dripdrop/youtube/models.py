from datetime import datetime
from dripdrop.authentication.models import User
from dripdrop.models.base import Base
from dripdrop.utils import get_current_time
from pydantic import Field, BaseModel
from sqlalchemy import (
    Column,
    String,
    TIMESTAMP,
    ForeignKey,
    Boolean,
    Integer,
)
from typing import Optional


class ApiBase(BaseModel):
    class Config:
        orm_mode = True


class GoogleAccounts(Base):
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


class GoogleAccount(ApiBase):
    email: str
    user_email: str
    access_token: str
    refresh_token: str
    expires: int
    subscriptions_loading: bool
    created_at: datetime
    last_updated: datetime


class YoutubeChannels(Base):
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


class YoutubeChannel(ApiBase):
    id: str
    title: str
    thumbnail: Optional[str] = Field(None)
    upload_playlist_id: Optional[str] = Field(None)
    created_at: datetime
    last_updated: datetime


class YoutubeSubscriptions(Base):
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


class YoutubeSubscription(ApiBase):
    id: str
    channel_id: str
    email: str
    published_at: datetime
    created_at: datetime


class YoutubeVideoCategories(Base):
    __tablename__ = "youtube_video_categories"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=get_current_time,
    )


class YoutubeVideoCategory(ApiBase):
    id: int
    name: str
    created_at: datetime


class YoutubeVideos(Base):
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


class YoutubeVideo(ApiBase):
    id: str
    title: str
    thumbnail: str
    channel_id: str
    category_id: int
    published_at: datetime
    created_at: datetime


class YoutubeVideoLikes(Base):
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


class YoutubeVideoLike(ApiBase):
    email: str
    video_id: str
    created_at: datetime


class YoutubeVideoQueues(Base):
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


class YoutubeVideoQueue(ApiBase):
    email: str
    video_id: str
    created_at: datetime


class YoutubeVideoWatches(Base):
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


class YoutubeVideoWatch(ApiBase):
    email: str
    video_id: str
    created_at: datetime
