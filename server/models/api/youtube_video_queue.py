from .base_model import Base
from datetime import datetime


class YoutubeVideoQueue(Base):
    email: str
    video_id: str
    created_at: datetime
