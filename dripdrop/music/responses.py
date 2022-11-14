from .models import MusicJob
from dripdrop.responses import ResponseBaseModel
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
    title: Optional[str]
    artist: Optional[str]
    album: Optional[str]
    grouping: Optional[str]
    artwork_url: Optional[str]


class JobsResponse(ResponseBaseModel):
    jobs: List[MusicJobResponse]
    total_pages: int


JobNotFoundResponse = "Job not found"


class JobUpdateResponse(ResponseBaseModel):
    type: Literal["COMPLETED", "STARTED"]
    job: MusicJobResponse
