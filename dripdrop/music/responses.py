from .models import MusicJob
from pydantic import BaseModel
from typing import Optional, List, Literal


class MusicChannelResponse(BaseModel):
    type: Literal["STARTED", "COMPLETED"]
    job_id: str


class GroupingResponse(BaseModel):
    grouping: str


class ArtworkUrlResponse(BaseModel):
    artwork_url: str


class TagsResponse(BaseModel):
    title: Optional[str]
    artist: Optional[str]
    album: Optional[str]
    grouping: Optional[str]
    artwork_url: Optional[str]


class JobsResponse(BaseModel):
    jobs: List[MusicJob]
    total_pages: int


class JobUpdateResponse(BaseModel):
    type: Literal["COMPLETED", "STARTED"]
    job: MusicJob
