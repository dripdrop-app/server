from typing import Optional

from fastapi import Form
from pydantic import BaseModel, HttpUrl


class CreateJobFormData(BaseModel):
    video_url: Optional[HttpUrl] = Form(None)
    artwork_url: Optional[str] = Form(None)
    title: str = Form(...)
    artist: str = Form(...)
    album: str = Form(...)
    grouping: Optional[str] = Form(None)
