from pydantic import BaseModel, Field
from server.models.main import YoutubeVideoCategory, YoutubeSubscription, YoutubeVideo
from typing import Literal, Optional, List

email_regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
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


class JobInfo(BaseModel):
    id: str
    filename: Optional[str]
    youtube_url: Optional[str] = Field(None, regex=youtube_regex)
    artwork_url: Optional[str]
    title: str
    artist: str
    album: str
    grouping: Optional[str]
    completed: bool
    failed: bool


class JobInfoResponse(ResponseBaseModel, JobInfo):
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

    class Download(JobInfoResponse):
        pass

    class AllJobs(ResponseBaseModel):
        jobs: List[JobInfoResponse]

    class JobUpdate(ResponseBaseModel):
        type: Literal["COMPLETED", "STARTED"]
        job: JobInfoResponse

    class CreateJob(ResponseBaseModel):
        job: JobInfoResponse


class YoutubeVideoCategoryResponse(ResponseBaseModel, YoutubeVideoCategory):
    pass


class YoutubeVideoResponse(ResponseBaseModel, YoutubeVideo):
    channel_title: str
    pass


class YoutubeSubscriptionResponse(ResponseBaseModel, YoutubeSubscription):
    channel_title: str
    channel_thumbnail: str
    pass


class YoutubeResponses:
    class Account(ResponseBaseModel):
        email: str
        refresh: bool

    class VideoCategories(ResponseBaseModel):
        categories: List[YoutubeVideoCategoryResponse]

    class Videos(ResponseBaseModel):
        total_videos: int
        videos: List[YoutubeVideoResponse]

    class Subscriptions(ResponseBaseModel):
        subscriptions: List[YoutubeSubscriptionResponse]
        total_subscriptions: int

    class SubscriptionUpdate(ResponseBaseModel):
        type = "SUBSCRIPITON_STATE"
        status: bool
