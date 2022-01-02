from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional, Union

email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
youtube_regex = r'^https:\/\/(www\.)?youtube\.com\/watch\?v=.+'


class User(BaseModel):
    email: str
    admin: bool
    authenticated: bool


class JobInfo(BaseModel):
    id: str
    filename: Optional[str]
    youtube_url: Optional[str] = Field(None, regex=youtube_regex)
    artwork_url: Optional[str]
    title: str
    artist: str
    album: str
    grouping: Optional[str]


class AuthRequests:
    class Login(BaseModel):
        email: str
        password: str

    class CreateAccount(BaseModel):
        email: str = Field(None, regex=email_regex)
        password: str = Field(None, min_length=8)


class AuthResponses:
    class User(BaseModel):
        email: str
        admin: bool

    class ValidError(BaseModel):
        error: str


class MusicResponses:
    class Grouping(BaseModel):
        grouping: str

    class ArtworkURL(BaseModel):
        artwork_url: str

    class Tags(BaseModel):
        title: Union[str, None]
        artist: Union[str, None]
        album: Union[str, None]
        grouping: Union[str, None]
        artwork_url: Union[str, None]

    class Download(JobInfo):
        pass


class YoutubeVideo(BaseModel):
    id: str
    title: str
    thumbnail: str
    channel_id: str
    published_at: datetime
    category_id: int
    created_at: datetime


class YoutubeResponses:
    class Account(BaseModel):
        email: str

    class Videos(BaseModel):
        videos: List[YoutubeVideo]
