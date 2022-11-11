from .models import YoutubeVideo, YoutubeSubscription, YoutubeVideoCategory
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List


class YoutubeVideoResponse(YoutubeVideo):
    channel_title: str
    channel_thumbnail: str
    liked: Optional[datetime]
    queued: Optional[datetime]
    watched: Optional[datetime]


class YoutubeSubscriptionResponse(YoutubeSubscription):
    channel_title: str
    channel_thumbnail: str


class AccountResponse(BaseModel):
    email: str
    refresh: bool


class VideoCategoriesResponse(BaseModel):
    categories: List[YoutubeVideoCategory]


class VideosResponse(BaseModel):
    videos: List[YoutubeVideoResponse]
    total_pages: int


class VideoResponse(BaseModel):
    video: YoutubeVideoResponse
    related_videos: List[YoutubeVideoResponse]


class VideoQueueResponse(BaseModel):
    prev: bool
    next: bool
    current_video: YoutubeVideoResponse


class SubscriptionsResponse(BaseModel):
    subscriptions: List[YoutubeSubscriptionResponse]


class SubscriptionUpdateResponse(BaseModel):
    type = "SUBSCRIPITON_STATE"
    status: bool
