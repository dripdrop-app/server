from .base_model import Base
from datetime import datetime
from typing import Optional


class YoutubeChannel(Base):
    id: str
    title: str
    thumbnail: Optional[str]
    upload_playlist_id: Optional[str]
    created_at: datetime
    last_updated: datetime
