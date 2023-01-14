from datetime import datetime
from pydantic import Field
from typing import Optional, List

from dripdrop.responses import ResponseBaseModel


class AccountResponse(ResponseBaseModel):
    email: str
    refresh: bool


class YoutubeChannelResponse(ResponseBaseModel):
    title: str
    thumbnail: str


class YoutubeSubscriptionResponse(ResponseBaseModel):
    channel_title: str
    channel_thumbnail: str


class SubscriptionsResponse(ResponseBaseModel):
    subscriptions: List[YoutubeSubscriptionResponse]
    total_pages: int


class YoutubeVideoCategoryResponse(ResponseBaseModel):
    id: int
    name: str


class YoutubeVideoCategoriesResponse(ResponseBaseModel):
    categories: list[YoutubeVideoCategoryResponse]


class YoutubeVideoResponse(ResponseBaseModel):
    title: str
    thumbnail: str
    category_id: int
    published_at: datetime
    channel_title: str
    channel_thumbnail: str
    liked: Optional[datetime] = Field(None)
    queued: Optional[datetime] = Field(None)
    watched: Optional[datetime] = Field(None)


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


class ErrorMessages:
    CHANNEL_NOT_FOUND = "Youtube Channel not found"
    PAGE_NOT_FOUND = "Page not found"
