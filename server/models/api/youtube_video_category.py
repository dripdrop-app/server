from .base_model import Base
from datetime import datetime


class YoutubeVideoCategory(Base):
    id: int
    name: str
    created_at: datetime
