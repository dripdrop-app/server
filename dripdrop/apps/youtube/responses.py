from datetime import datetime
from pydantic import Field
from typing import Optional, List

from dripdrop.responses import ResponseBaseModel

from .models import YoutubeVideo, YoutubeSubscription, YoutubeVideoCategory


class YoutubeVideoResponse(ResponseBaseModel, YoutubeVideo):
    channel_title: str
    channel_thumbnail: str
    liked: Optional[datetime] = Field(None)
    queued: Optional[datetime] = Field(None)
    watched: Optional[datetime] = Field(None)


class YoutubeSubscriptionResponse(ResponseBaseModel, YoutubeSubscription):
    channel_title: str
    channel_thumbnail: str


class AccountResponse(ResponseBaseModel):
    email: str
    refresh: bool


class VideoCategoriesResponse(ResponseBaseModel):
    categories: List[YoutubeVideoCategory]


class VideosResponse(ResponseBaseModel):
    videos: List[YoutubeVideoResponse]
    total_pages: int


class VideoResponse(ResponseBaseModel):
    video: YoutubeVideoResponse
    related_videos: List[YoutubeVideoResponse]


class VideoQueueResponse(ResponseBaseModel):
    prev: bool
    next: bool
    current_video: YoutubeVideoResponse


class SubscriptionsResponse(ResponseBaseModel):
    subscriptions: List[YoutubeSubscriptionResponse]
    total_pages: int


class SubscriptionUpdateResponse(ResponseBaseModel):
    type = "SUBSCRIPITON_STATE"
    status: bool
