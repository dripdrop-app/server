from pydantic import BaseModel, Field
from server.models import YoutubeVideoCategory, YoutubeSubscription, YoutubeVideo
from typing import Optional, List

email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
youtube_regex = r'^https:\/\/(www\.)?youtube\.com\/watch\?v=.+'


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
        title: Optional[str]
        artist: Optional[str]
        album: Optional[str]
        grouping: Optional[str]
        artwork_url: Optional[str]

    class Download(JobInfo):
        pass


class YoutubeResponses:
    class Account(BaseModel):
        email: str

    class Videos(BaseModel):
        total_videos: int
        categories: List[YoutubeVideoCategory]
        videos: List[YoutubeVideo]

    class Subscriptions(BaseModel):
        subscriptions: List[YoutubeSubscription]
        total_subscriptions: int
