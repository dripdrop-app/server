from .google_account import GoogleAccount
from .music_job import MusicJob
from .session import Session
from .user import User, SessionUser
from .youtube_channel import YoutubeChannel
from .youtube_subscription import YoutubeSubscription
from .youtube_video_category import YoutubeVideoCategory
from .youtube_video_like import YoutubeVideoLike
from .youtube_video_watch import YoutubeVideoWatch
from .youtube_video import YoutubeVideo
from datetime import datetime
from pydantic import BaseModel
from typing import Literal, Optional, List


youtube_regex = r"^https:\/\/(www\.)?youtube\.com\/watch\?v=.+"


def _snake_to_camel(string: str):
    field_parts = string.split("_")
    new_field = ""
    for i, part in enumerate(field_parts):
        if i == 0:
            new_field += part
        else:
            new_field += part.capitalize()
    return new_field


class _ResponseBaseModel(BaseModel):
    class Config:
        alias_generator = _snake_to_camel
        allow_population_by_field_name = True


class RedisResponses:
    class MusicChannel(BaseModel):
        job_id: str
        type: Literal["STARTED", "COMPLETED"]


class MusicJobResponse(_ResponseBaseModel, MusicJob):
    pass


class AuthResponses:
    class User(_ResponseBaseModel):
        email: str
        admin: bool

    class ValidError(_ResponseBaseModel):
        error: str


class MusicResponses:
    class Grouping(_ResponseBaseModel):
        grouping: str

    class ArtworkURL(_ResponseBaseModel):
        artwork_url: str

    class Tags(_ResponseBaseModel):
        title: Optional[str]
        artist: Optional[str]
        album: Optional[str]
        grouping: Optional[str]
        artwork_url: Optional[str]

    class AllJobs(_ResponseBaseModel):
        jobs: List[MusicJobResponse]
        total_pages: int

    class JobUpdate(_ResponseBaseModel):
        type: Literal["COMPLETED", "STARTED"]
        job: MusicJobResponse


class YoutubeVideoCategoryResponse(_ResponseBaseModel, YoutubeVideoCategory):
    pass


class _YoutubeVideoResponse(_ResponseBaseModel, YoutubeVideo):
    channel_title: str
    channel_thumbnail: str
    liked: Optional[datetime]
    queued: Optional[datetime]
    watched: Optional[datetime]


class _YoutubeSubscriptionResponse(_ResponseBaseModel, YoutubeSubscription):
    channel_title: str
    channel_thumbnail: str


class YoutubeResponses:
    class Account(_ResponseBaseModel):
        email: str
        refresh: bool

    class VideoCategories(_ResponseBaseModel):
        categories: List[YoutubeVideoCategoryResponse]

    class Videos(_ResponseBaseModel):
        videos: List[_YoutubeVideoResponse]
        total_pages: int

    class Video(_ResponseBaseModel):
        video: _YoutubeVideoResponse
        related_videos: List[_YoutubeVideoResponse]

    class VideoQueue(_ResponseBaseModel):
        prev: bool
        next: bool
        current_video: _YoutubeVideoResponse

    class Subscriptions(_ResponseBaseModel):
        subscriptions: List[_YoutubeSubscriptionResponse]

    class SubscriptionUpdate(_ResponseBaseModel):
        type = "SUBSCRIPITON_STATE"
        status: bool


__all__ = [
    GoogleAccount,
    MusicJob,
    Session,
    User,
    SessionUser,
    YoutubeChannel,
    YoutubeSubscription,
    YoutubeVideoCategory,
    YoutubeVideoLike,
    YoutubeVideoWatch,
    YoutubeVideo,
    youtube_regex,
    RedisResponses,
    MusicJobResponse,
    AuthResponses,
    MusicResponses,
    YoutubeResponses,
]
