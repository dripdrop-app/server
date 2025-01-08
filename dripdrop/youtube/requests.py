from typing import Optional

from pydantic import BaseModel, Field


class VideosQueryParams(BaseModel):
    video_categories: Optional[str] = Field("")
    channel_id: Optional[str] = Field(None)
    liked_only: Optional[bool] = Field(False)
    queued_only: Optional[bool] = Field(False)
