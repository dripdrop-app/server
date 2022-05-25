from datetime import datetime
from pydantic import BaseModel
from server.models.main import (
    MusicJob,
    YoutubeVideoCategory,
    YoutubeSubscription,
    YoutubeVideo,
)
from typing import Literal, Optional, List

youtube_regex = r"^https:\/\/(www\.)?youtube\.com\/watch\?v=.+"


def snake_to_camel(string: str):
    field_parts = string.split("_")
    new_field = ""
    for i, part in enumerate(field_parts):
        if i == 0:
            new_field += part
        else:
            new_field += part.capitalize()
    return new_field


class ResponseBaseModel(BaseModel):
    class Config:
        alias_generator = snake_to_camel
        allow_population_by_field_name = True


class RedisResponses:
    class MusicChannel(BaseModel):
        job_id: str
        type: Literal["STARTED", "COMPLETED"]


class MusicJobResponse(ResponseBaseModel, MusicJob):
    pass


class AuthResponses:
    class User(ResponseBaseModel):
        email: str
        admin: bool

    class ValidError(ResponseBaseModel):
        error: str


class MusicResponses:
    class Grouping(ResponseBaseModel):
        grouping: str

    class ArtworkURL(ResponseBaseModel):
        artwork_url: str

    class Tags(ResponseBaseModel):
        title: Optional[str]
        artist: Optional[str]
        album: Optional[str]
        grouping: Optional[str]
        artwork_url: Optional[str]

    class Download(MusicJobResponse):
        pass

    class AllJobs(ResponseBaseModel):
        jobs: List[MusicJobResponse]

    class JobUpdate(ResponseBaseModel):
        type: Literal["COMPLETED", "STARTED"]
        job: MusicJobResponse


class YoutubeVideoCategoryResponse(ResponseBaseModel, YoutubeVideoCategory):
    pass


class YoutubeVideoResponse(ResponseBaseModel, YoutubeVideo):
    channel_title: str
    liked: Optional[datetime]
    queued: Optional[datetime]
    watched: Optional[datetime]


class YoutubeSubscriptionResponse(ResponseBaseModel, YoutubeSubscription):
    channel_title: str
    channel_thumbnail: str


class YoutubeResponses:
    class Account(ResponseBaseModel):
        email: str
        refresh: bool

    class VideoCategories(ResponseBaseModel):
        categories: List[YoutubeVideoCategoryResponse]

    class Videos(ResponseBaseModel):
        videos: List[YoutubeVideoResponse]

    class Video(ResponseBaseModel):
        video: YoutubeVideoResponse
        related_videos: List[YoutubeVideoResponse]

    class VideoQueue(ResponseBaseModel):
        prev: bool
        next: bool
        current_video: YoutubeVideoResponse

    class Subscriptions(ResponseBaseModel):
        subscriptions: List[YoutubeSubscriptionResponse]

    class SubscriptionUpdate(ResponseBaseModel):
        type = "SUBSCRIPITON_STATE"
        status: bool
