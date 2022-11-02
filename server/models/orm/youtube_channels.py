from .base_model import Base
from sqlalchemy import Column, String, text, TIMESTAMP
from sqlalchemy.orm import relationship


class YoutubeChannels(Base):
    __tablename__ = "youtube_channels"
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    thumbnail = Column(String, nullable=True)
    upload_playlist_id = Column(String, nullable=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )
    last_updated = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_onupdate=text("NOW()"),
    )
    subscriptions = relationship("YoutubeSubscriptions", back_populates="channel")
    videos = relationship("YoutubeVideos", back_populates="channel")
