from pydantic import Field
from typing import Optional, List, Literal

from dripdrop.responses import ResponseBaseModel


class MusicJobResponse(ResponseBaseModel):
    artwork_url: Optional[str] = Field(None)
    artwork_filename: Optional[str] = Field(None)
    original_filename: Optional[str] = Field(None)
    filename_url: Optional[str] = Field(None)
    youtube_url: Optional[str] = Field(None)
    download_filename: Optional[str] = Field(None)
    download_url: Optional[str] = Field(None)
    title: str
    artist: str
    album: str
    grouping: Optional[str] = Field(None)
    completed: bool
    failed: bool

    # Add root validator to fix filenames (remove all slashes except last)


class MusicChannelResponse(ResponseBaseModel):
    type: Literal["STARTED", "COMPLETED"]
    job_id: str


class GroupingResponse(ResponseBaseModel):
    grouping: str


class ArtworkUrlResponse(ResponseBaseModel):
    artwork_url: str


class TagsResponse(ResponseBaseModel):
    title: Optional[str] = Field(None)
    artist: Optional[str] = Field(None)
    album: Optional[str] = Field(None)
    grouping: Optional[str] = Field(None)
    artwork_url: Optional[str] = Field(None)


class JobsResponse(ResponseBaseModel):
    jobs: List[MusicJobResponse]
    total_pages: int


class JobUpdateResponse(ResponseBaseModel):
    type: Literal["COMPLETED", "STARTED"]
    job: MusicJobResponse


class ErrorMessages:
    JOB_NOT_FOUND = "Job not found"
    GROUPING_ERROR = "Unable to get grouping"
    ARTWORK_ERROR = "Unable to get artwork"
