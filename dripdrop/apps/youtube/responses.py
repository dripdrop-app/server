from datetime import datetime
from pydantic import Field
from typing import Optional, List

from dripdrop.responses import ResponseBaseModel


class AccountResponse(ResponseBaseModel):
    email: str
    refresh: bool


class YoutubeChannelResponse(ResponseBaseModel):
    id: str
    title: str
    thumbnail: str | None


class YoutubeSubscriptionResponse(ResponseBaseModel):
    channel_id: str
    channel_title: str
    channel_thumbnail: str | None
    published_at: datetime


class SubscriptionsResponse(ResponseBaseModel):
    subscriptions: List[YoutubeSubscriptionResponse]
    total_pages: int


class YoutubeVideoCategoryResponse(ResponseBaseModel):
    id: int
    name: str


class YoutubeVideoCategoriesResponse(ResponseBaseModel):
    categories: list[YoutubeVideoCategoryResponse]


class YoutubeVideoResponse(ResponseBaseModel):
    id: str
    title: str
    thumbnail: str
    category_id: int
    published_at: datetime
    channel_id: str
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
    VIDEO_CATEGORIES_INVALID = "Video Categories must be an integer"
    VIDEO_NOT_FOUND = "Video not found"
    ADD_VIDEO_WATCH_ERROR = "Could not add video watch"
    ADD_VIDEO_LIKE_ERROR = "Could not add video like"
    REMOVE_VIDEO_LIKE_ERROR = "Could not remove video like"
    ADD_VIDEO_QUEUE_ERROR = "Could not add video to queue"
    REMOVE_VIDEO_QUEUE_ERROR = "Could not delete video queue"
    VIDEO_QUEUE_NOT_FOUND = "Video in queue not found"
