import databases
import sqlalchemy
from datetime import datetime
from pydantic import BaseModel, SecretStr
from sqlalchemy.sql.expression import text
from sqlalchemy.ext.declarative import declarative_base
from server.config import config
from typing import Optional


DATABASE_URL = config.database_url


def init_db():
    return databases.Database(DATABASE_URL)


db = init_db()
metadata = sqlalchemy.MetaData()
Base = declarative_base(metadata=metadata)


class Users(Base):
    __tablename__ = "users"
    email = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    password = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    admin = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    approved = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    created_at = sqlalchemy.Column(
        sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True),
        server_default=text("NOW()"),
    )


class User(BaseModel):
    email: str
    password: SecretStr
    admin: bool
    approved: bool
    created_at: datetime


SessionUser = Optional[User]


class Sessions(Base):
    __tablename__ = "sessions"
    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    user_email = sqlalchemy.Column(
        sqlalchemy.ForeignKey(
            Users.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="sessions_user_email_fkey",
        ),
        nullable=False,
    )
    created_at = sqlalchemy.Column(
        sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True),
        server_default=text("NOW()"),
    )


class Session(BaseModel):
    id: str
    user_email: str
    created_at: datetime


class MusicJobs(Base):
    __tablename__ = "music_jobs"
    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    user_email = sqlalchemy.Column(
        sqlalchemy.ForeignKey(
            Users.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="music_jobs_user_email_fkey",
        ),
        nullable=False,
    )
    filename = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    youtube_url = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    artwork_url = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    artist = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    album = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    grouping = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    completed = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    failed = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    created_at = sqlalchemy.Column(
        sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True),
        server_default=text("NOW()"),
    )


class MusicJob(BaseModel):
    id: str
    user_email: str
    filename: Optional[str] = ""
    youtube_url: Optional[str]
    artwork_url: Optional[str]
    title: str
    artist: str
    album: str
    grouping: Optional[str]
    completed: bool
    failed: bool
    created_at: datetime


class GoogleAccounts(Base):
    __tablename__ = "google_accounts"
    email = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    user_email = sqlalchemy.Column(
        sqlalchemy.ForeignKey(
            Users.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="google_accounts_user_email_fkey",
        ),
        nullable=False,
    )
    access_token = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    refresh_token = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    expires = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    subscriptions_loading = sqlalchemy.Column(
        sqlalchemy.Boolean, nullable=False, server_default="0"
    )
    created_at = sqlalchemy.Column(
        sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True),
        server_default=text("NOW()"),
    )
    last_updated = sqlalchemy.Column(
        sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True),
        server_default=text("NOW()"),
    )


class GoogleAccount(BaseModel):
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
    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    thumbnail = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    upload_playlist_id = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_at = sqlalchemy.Column(
        sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True),
        server_default=text("NOW()"),
    )
    last_updated = sqlalchemy.Column(
        sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True),
        server_default=text("NOW()"),
        server_onupdate=text("NOW()"),
    )


class YoutubeChannel(BaseModel):
    id: str
    title: str
    thumbnail: Optional[str]
    upload_playlist_id: Optional[str]
    created_at: datetime
    last_updated: datetime


class YoutubeSubscriptions(Base):
    __tablename__ = "youtube_subscriptions"
    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    channel_id = sqlalchemy.Column(
        sqlalchemy.ForeignKey(
            YoutubeChannels.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_subscriptions_channel_id_fkey",
        ),
        nullable=False,
    )
    email = sqlalchemy.Column(
        sqlalchemy.ForeignKey(
            GoogleAccounts.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_subscriptions_email_fkey",
        ),
        nullable=False,
    )
    published_at = sqlalchemy.Column(
        sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True)
    )
    created_at = sqlalchemy.Column(
        sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True),
        server_default=text("NOW()"),
    )


class YoutubeSubscription(BaseModel):
    id: str
    channel_id: str
    email: str
    published_at: datetime
    created_at: datetime


class YoutubeVideoCategories(Base):
    __tablename__ = "youtube_video_categories"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    created_at = sqlalchemy.Column(
        sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True),
        server_default=text("NOW()"),
    )


class YoutubeVideoCategory(BaseModel):
    id: int
    name: str
    created_at: datetime


class YoutubeVideos(Base):
    __tablename__ = "youtube_videos"
    id = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    thumbnail = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    channel_id = sqlalchemy.Column(
        sqlalchemy.ForeignKey(
            YoutubeChannels.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_videos_channel_id_fkey",
        ),
        nullable=False,
    )
    category_id = sqlalchemy.Column(
        sqlalchemy.ForeignKey(
            YoutubeVideoCategories.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_videos_category_id_fkey",
        ),
        nullable=False,
    )
    published_at = sqlalchemy.Column(sqlalchemy.TIMESTAMP(timezone=True))
    created_at = sqlalchemy.Column(
        sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True),
        server_default=text("NOW()"),
    )


class YoutubeVideo(BaseModel):
    id: str
    title: str
    thumbnail: str
    channel_id: str
    category_id: int
    published_at: datetime
    created_at: datetime


class YoutubeVideoLikes(Base):
    __tablename__ = "youtube_video_likes"
    email = sqlalchemy.Column(
        sqlalchemy.ForeignKey(
            GoogleAccounts.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_video_likes_email_fkey",
        ),
        primary_key=True,
        nullable=False,
    )
    video_id = sqlalchemy.Column(
        sqlalchemy.ForeignKey(
            YoutubeVideos.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_video_likes_video_id_fkey",
        ),
        primary_key=True,
        nullable=False,
    )
    created_at = sqlalchemy.Column(
        sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True),
        server_default=text("NOW()"),
    )


class YoutubeVideoLike(BaseModel):
    email: str
    video_id: str
    created_at: datetime


class YoutubeVideoQueues(Base):
    __tablename__ = "youtube_video_queues"
    email = sqlalchemy.Column(
        sqlalchemy.ForeignKey(
            GoogleAccounts.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_video_queues_email_fkey",
        ),
        primary_key=True,
        nullable=False,
    )
    video_id = sqlalchemy.Column(
        sqlalchemy.ForeignKey(
            YoutubeVideos.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_video_queues_video_id_fkey",
        ),
        primary_key=True,
        nullable=False,
    )
    created_at = sqlalchemy.Column(
        sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True),
        server_default=text("NOW()"),
    )


class YoutubeVideoQueue(BaseModel):
    email: str
    video_id: str
    created_at: datetime
