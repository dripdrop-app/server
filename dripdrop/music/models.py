import re
from datetime import datetime
from dripdrop.authentication.models import User
from dripdrop.services.boto3 import boto3_service
from dripdrop.utils import get_current_time
from pydantic import Field, root_validator, BaseModel
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base
from typing import Optional

youtube_regex = r"^https:\/\/(www\.)?youtube\.com\/watch\?v=.+"

Base = declarative_base()


class ApiBase(BaseModel):
    class Config:
        orm_mode = True


class MusicJobs(Base):
    __tablename__ = "music_jobs"
    id = Column(String, primary_key=True)
    user_email = Column(
        ForeignKey(
            User.email,
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
        default=get_current_time,
    )
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)


class MusicJob(ApiBase):
    id: str
    user_email: str
    filename: Optional[str] = Field(None)
    original_filename: Optional[str] = Field(None)
    youtube_url: Optional[str] = Field(None)
    download_url: Optional[str] = Field(None)
    download_filename: Optional[str] = Field(None)
    artwork_url: Optional[str] = Field(None)
    artwork_filename: Optional[str] = Field(None)
    title: str
    artist: str
    album: str
    grouping: Optional[str]
    completed: bool
    failed: bool
    created_at: datetime

    @root_validator()
    def resolve_url(cls, values):
        id = values["id"]

        def _resolve_url(key: str = ..., resolver=...):
            value = values.get(key)
            if value and not re.search("^http(s)?://", value):
                values[key] = resolver(filename=f"{id}/{value}")
                if key == "artwork_url":
                    values["artwork_filename"] = value
                elif key == "download_url":
                    values["download_filename"] = value
                elif key == "filename":
                    values["original_filename"] = value

        _resolve_url(key="artwork_url", resolver=boto3_service.resolve_artwork_url)
        _resolve_url(key="download_url", resolver=boto3_service.resolve_music_url)
        _resolve_url(key="filename", resolver=boto3_service.resolve_music_url)
        return values
