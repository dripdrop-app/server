from .base_model import Base
from datetime import datetime


class YoutubeVideo(Base):
    id: str
    title: str
    thumbnail: str
    channel_id: str
    category_id: int
    published_at: datetime
    created_at: datetime
