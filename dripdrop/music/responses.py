from .models import MusicJob
from dripdrop.responses import ResponseBaseModel
from pydantic import Field
from typing import Optional, List, Literal


class MusicJobResponse(ResponseBaseModel, MusicJob):
    pass


class MusicChannelResponse(ResponseBaseModel):
    type: Literal["STARTED", "COMPLETED"]
    job_id: str


class GroupingResponse(ResponseBaseModel):
    grouping: str


GroupingErrorResponse = "Unable to get grouping"


class ArtworkUrlResponse(ResponseBaseModel):
    artwork_url: str


ArtworkErrorResponse = "Unable to get artwork"


class TagsResponse(ResponseBaseModel):
    title: Optional[str] = Field(None)
    artist: Optional[str] = Field(None)
    album: Optional[str] = Field(None)
    grouping: Optional[str] = Field(None)
    artwork_url: Optional[str] = Field(None)


class JobsResponse(ResponseBaseModel):
    jobs: List[MusicJobResponse]
    total_pages: int


JobNotFoundResponse = "Job not found"


class JobUpdateResponse(ResponseBaseModel):
    type: Literal["COMPLETED", "STARTED"]
    job: MusicJobResponse
