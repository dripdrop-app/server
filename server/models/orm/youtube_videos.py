from .base_model import Base
from .youtube_channels import YoutubeChannels
from .youtube_video_categories import YoutubeVideoCategories
from sqlalchemy import Column, String, text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship


class YoutubeVideos(Base):
    __tablename__ = "youtube_videos"
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    thumbnail = Column(String, nullable=False)
    channel_id = Column(
        ForeignKey(
            YoutubeChannels.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_videos_channel_id_fkey",
        ),
        nullable=False,
    )
    category_id = Column(
        ForeignKey(
            YoutubeVideoCategories.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_videos_category_id_fkey",
        ),
        nullable=False,
    )
    published_at = Column(TIMESTAMP(timezone=True), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )
    channel = relationship("YoutubeChannels", back_populates="videos")
    category = relationship("YoutubeVideoCategories", back_populates="videos")
    likes = relationship("YoutubeVideoLikes", back_populates="video")
    queues = relationship("YoutubeVideoQueues", back_populates="video")
    watches = relationship("YoutubeVideoWatches", back_populates="video")
