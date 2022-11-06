from .base_model import Base
from .google_accounts import GoogleAccounts
from .youtube_videos import YoutubeVideos
from sqlalchemy import Column, ForeignKey, TIMESTAMP, text
from sqlalchemy.orm import relationship


class YoutubeVideoQueues(Base):
    __tablename__ = "youtube_video_queues"
    email = Column(
        ForeignKey(
            GoogleAccounts.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_video_queues_email_fkey",
        ),
        primary_key=True,
        nullable=False,
    )
    video_id = Column(
        ForeignKey(
            YoutubeVideos.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_video_queues_video_id_fkey",
        ),
        primary_key=True,
        nullable=False,
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )
    google_account = relationship("GoogleAccounts", back_populates="queues")
    video = relationship("YoutubeVideos", back_populates="queues")