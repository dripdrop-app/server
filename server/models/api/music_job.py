import re
from .base_model import Base
from datetime import datetime
from server.services.boto3 import boto3_service
from typing import Optional


class MusicJob(Base):
    id: str
    user_email: str
    filename: Optional[str]
    youtube_url: Optional[str]
    download_url: Optional[str]
    artwork_url: Optional[str]
    title: str
    artist: str
    album: str
    grouping: Optional[str]
    completed: bool
    failed: bool
    created_at: datetime

    def __init__(self, **data) -> None:
        super().__init__(**data)
        if data.get("artwork_url") and not re.search(
            "^http(s)?://", data["artwork_url"]
        ):
            self.artwork_url = boto3_service.resolve_artwork_url(
                filename=data["artwork_url"]
            )
        if data.get("download_url") and not re.search(
            "^http(s)?://", data["download_url"]
        ):
            self.download_url = boto3_service.resolve_music_url(
                filename=data["download_url"]
            )
