from .base_model import Base
from .users import Users
from sqlalchemy import Column, String, text, TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.orm import relationship


class MusicJobs(Base):
    __tablename__ = "music_jobs"
    id = Column(String, primary_key=True)
    user_email = Column(
        ForeignKey(
            Users.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="music_jobs_user_email_fkey",
        ),
        nullable=False,
    )
    filename = Column(String, nullable=True)
    youtube_url = Column(String, nullable=True)
    download_url = Column(String, nullable=True)
    artwork_url = Column(String, nullable=True)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    album = Column(String, nullable=False)
    grouping = Column(String, nullable=True)
    completed = Column(Boolean, nullable=False)
    failed = Column(Boolean, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )
    user = relationship("Users", back_populates="music_jobs")
