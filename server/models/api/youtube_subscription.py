from .base_model import Base
from datetime import datetime


class YoutubeSubscription(Base):
    id: str
    channel_id: str
    email: str
    published_at: datetime
    created_at: datetime
