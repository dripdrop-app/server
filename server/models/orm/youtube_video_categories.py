from .base_model import Base
from sqlalchemy import Column, String, text, TIMESTAMP, Integer
from sqlalchemy.orm import relationship


class YoutubeVideoCategories(Base):
    __tablename__ = "youtube_video_categories"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )
    videos = relationship("YoutubeVideos", back_populates="category")
