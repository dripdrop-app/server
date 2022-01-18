import databases
import sqlalchemy
from datetime import datetime
from pydantic import BaseModel, Field
from sqlalchemy.sql.expression import text
from server.config import config
from typing import List, Optional, Union

DATABASE_URL = config.database_url
db = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    'users',
    metadata,
    sqlalchemy.Column("email", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("password", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("admin", sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column("approved", sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column(
        "created_at", sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True), server_default=text("NOW()")),
)


class User(BaseModel):
    email: str
    password: str
    admin: bool
    approved: bool
    created_at: datetime


sessions = sqlalchemy.Table(
    'sessions',
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("user_email", sqlalchemy.ForeignKey(
        users.c.email, onupdate='CASCADE', ondelete='CASCADE'), nullable=False),
    sqlalchemy.Column("created_at", sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True),
                      server_default=text("NOW()"))
)


class Session(BaseModel):
    id: str
    user_email: str
    created_at: datetime


music_jobs = sqlalchemy.Table(
    'music_jobs',
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("user_email", sqlalchemy.ForeignKey(
        users.c.email, onupdate='CASCADE', ondelete='CASCADE'), nullable=False),
    sqlalchemy.Column("filename", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("youtube_url", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("artwork_url", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("title", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("artist", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("album", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("grouping", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("completed", sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column("failed", sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column("created_at", sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True),
                      server_default=text("NOW()"))
)


class MusicJob(BaseModel):
    id: str
    user_email: str
    filename: Union[str, None] = ''
    youtube_url: Union[str, None]
    artwork_url: Union[str, None]
    title: str
    artist: str
    album: str
    grouping: Union[str, None]
    completed: bool
    failed: bool
    created_at: datetime


google_accounts = sqlalchemy.Table(
    'google_accounts',
    metadata,
    sqlalchemy.Column("email", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("user_email", sqlalchemy.ForeignKey(
        users.c.email, onupdate='CASCADE', ondelete='CASCADE'), nullable=False),
    sqlalchemy.Column("access_token", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("refresh_token", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("expires", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("subscriptions_loading",
                      sqlalchemy.Boolean, nullable=False, server_default='0'),
    sqlalchemy.Column(
        "created_at", sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True), server_default=text("NOW()")),
    sqlalchemy.Column(
        "last_updated", sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True), server_default=text("NOW()"))
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


youtube_channels = sqlalchemy.Table(
    'youtube_channels',
    metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("thumbnail", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("upload_playlist_id", sqlalchemy.String, nullable=True),
    sqlalchemy.Column("created_at", sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True),
                      server_default=text("NOW()")),
    sqlalchemy.Column("last_updated", sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True), server_default=text("NOW()"),
                      server_onupdate=text("NOW()"))
)


class YoutubeChannel(BaseModel):
    id: str
    title: str
    thumbnail: Union[str, None]
    upload_playlist_id: Union[str, None]
    created_at: datetime
    last_updated: datetime


youtube_subscriptions = sqlalchemy.Table(
    'youtube_subscriptions',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String, primary_key=True),
    sqlalchemy.Column('channel_id', sqlalchemy.ForeignKey(
        youtube_channels.c.id, onupdate='CASCADE', ondelete='CASCADE'), nullable=False),
    sqlalchemy.Column('email', sqlalchemy.ForeignKey(
        google_accounts.c.email, onupdate='CASCADE', ondelete='CASCADE'), nullable=False),
    sqlalchemy.Column(
        'published_at', sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True)),
    sqlalchemy.Column(
        'created_at', sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True), server_default=text('NOW()')),
)


class YoutubeSubscription(BaseModel):
    id: str
    channel_id: str
    email: str
    published_at: datetime
    created_at: datetime


youtube_video_categories = sqlalchemy.Table(
    'youtube_video_categories',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('name', sqlalchemy.String, nullable=False),
    sqlalchemy.Column(
        'created_at', sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True), server_default=text('NOW()')),
)


class YoutubeVideoCategory(BaseModel):
    id: int
    name: str
    created_at: datetime


youtube_videos = sqlalchemy.Table(
    'youtube_videos',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.String, primary_key=True),
    sqlalchemy.Column('title', sqlalchemy.String, nullable=False),
    sqlalchemy.Column('thumbnail', sqlalchemy.String, nullable=False),
    sqlalchemy.Column('channel_id', sqlalchemy.ForeignKey(
        youtube_channels.c.id, onupdate='CASCADE', ondelete='CASCADE'), nullable=False),
    sqlalchemy.Column('published_at', sqlalchemy.TIMESTAMP(timezone=True)),
    sqlalchemy.Column('category_id', sqlalchemy.ForeignKey(
        youtube_video_categories.c.id, onupdate='CASCADE', ondelete='CASCADE'), nullable=False),
    sqlalchemy.Column(
        'created_at', sqlalchemy.dialects.postgresql.TIMESTAMP(timezone=True), server_default=text('NOW()')),
)


class YoutubeVideo(BaseModel):
    id: str
    title: str
    thumbnail: str
    channel_id: str
    published_at: datetime
    category_id: int
    created_at: datetime


email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
youtube_regex = r'^https:\/\/(www\.)?youtube\.com\/watch\?v=.+'


class SessionUser(BaseModel):
    email: str
    admin: bool
    authenticated: bool


class JobInfo(BaseModel):
    id: str
    filename: Optional[str]
    youtube_url: Optional[str] = Field(None, regex=youtube_regex)
    artwork_url: Optional[str]
    title: str
    artist: str
    album: str
    grouping: Optional[str]


class AuthRequests:
    class Login(BaseModel):
        email: str
        password: str

    class CreateAccount(BaseModel):
        email: str = Field(None, regex=email_regex)
        password: str = Field(None, min_length=8)


class AuthResponses:
    class User(BaseModel):
        email: str
        admin: bool

    class ValidError(BaseModel):
        error: str


class MusicResponses:
    class Grouping(BaseModel):
        grouping: str

    class ArtworkURL(BaseModel):
        artwork_url: str

    class Tags(BaseModel):
        title: Union[str, None]
        artist: Union[str, None]
        album: Union[str, None]
        grouping: Union[str, None]
        artwork_url: Union[str, None]

    class Download(JobInfo):
        pass


class YoutubeVideo(BaseModel):
    id: str
    title: str
    thumbnail: str
    channel_id: str
    published_at: datetime
    category_id: int
    created_at: datetime


class YoutubeResponses:
    class Account(BaseModel):
        email: str

    class Videos(BaseModel):
        total_videos: int
        categories: List[YoutubeVideoCategory]
        videos: List[YoutubeVideo]

    class Subscriptions(BaseModel):
        subscriptions: List[YoutubeSubscription]
        total_subscriptions: int
