from datetime import datetime
from typing import List, Literal, Optional

from pydantic import Field, field_validator

from dripdrop.base.responses import ResponseBaseModel


class MusicJobResponse(ResponseBaseModel):
    id: str
    artwork_url: Optional[str] = Field(None)
    artwork_filename: Optional[str] = Field(None)
    original_filename: Optional[str] = Field(None)
    filename_url: Optional[str] = Field(None)
    video_url: Optional[str] = Field(None)
    download_filename: Optional[str] = Field(None)
    download_url: Optional[str] = Field(None)
    title: str
    artist: str
    album: str
    grouping: Optional[str] = Field(None)
    completed: bool
    failed: bool
    created_at: datetime

    @field_validator("artwork_filename", "original_filename", "download_filename")
    def fix_filename(cls, value):
        if value:
            return value.split("/")[-1]
        return value


class MusicJobUpdateResponse(ResponseBaseModel):
    id: str
    status: Literal["STARTED", "COMPLETED"]


class GroupingResponse(ResponseBaseModel):
    grouping: str


class ResolvedArtworkUrlResponse(ResponseBaseModel):
    resolved_artwork_url: str


class TagsResponse(ResponseBaseModel):
    title: Optional[str] = Field(None)
    artist: Optional[str] = Field(None)
    album: Optional[str] = Field(None)
    grouping: Optional[str] = Field(None)
    artwork_url: Optional[str] = Field(None)


class MusicJobsResponse(ResponseBaseModel):
    music_jobs: List[MusicJobResponse]
    total_pages: int


class ErrorMessages:
    JOB_NOT_FOUND = "Job not found"
    DOWNLOAD_NOT_FOUND = "Download not found"
    GROUPING_ERROR = "Unable to get grouping"
    ARTWORK_ERROR = "Unable to get artwork"
    PAGE_NOT_FOUND = "Page not found"
    CREATE_JOB_BOTH_DEFINED = "'file' and 'video_url' cannot both be defined"
    CREATE_JOB_NOT_DEFINED = "'file' or 'video_url' must be defined"
    FILE_INCORRECT_FORMAT = "File is incorrect format"
    FAILED_AUDIO_FILE_UPLOAD = "Failed to upload audio file"
    FAILED_IMAGE_UPLOAD = "Failed to upload artwork"
