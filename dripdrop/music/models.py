import re
from datetime import datetime
from dripdrop.authentication.models import Users
from dripdrop.models import ApiBase, OrmBase
from dripdrop.services.boto3 import boto3_service
from sqlalchemy import Column, String, text, TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from typing import Optional

youtube_regex = r"^https:\/\/(www\.)?youtube\.com\/watch\?v=.+"


class MusicJobs(OrmBase):
    __tablename__ = "music_jobs"
    id = Column(String, primary_key=True)
    user_email = Column(
        ForeignKey(
            Users.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="music_jobs_user_email_fkey",
        ),
        nullable=False,
    )
    filename = Column(String, nullable=True)
    youtube_url = Column(String, nullable=True)
    download_url = Column(String, nullable=True)
    artwork_url = Column(String, nullable=True)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    album = Column(String, nullable=False)
    grouping = Column(String, nullable=True)
    completed = Column(Boolean, nullable=False)
    failed = Column(Boolean, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)
    user = relationship("Users", back_populates="music_jobs")


class MusicJob(ApiBase):
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
