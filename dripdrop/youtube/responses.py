from .models import YoutubeVideo, YoutubeSubscription, YoutubeVideoCategory
from datetime import datetime
from dripdrop.responses import ResponseBaseModel
from typing import Optional, List


class YoutubeVideoResponse(ResponseBaseModel, YoutubeVideo):
    channel_title: str
    channel_thumbnail: str
    liked: Optional[datetime]
    queued: Optional[datetime]
    watched: Optional[datetime]


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


class SubscriptionUpdateResponse(ResponseBaseModel):
    type = "SUBSCRIPITON_STATE"
    status: bool
