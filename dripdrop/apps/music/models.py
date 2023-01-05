from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Boolean

from dripdrop.apps.authentication.models import User
from dripdrop.models.base import Base
from dripdrop.utils import get_current_time

youtube_regex = r"^https:\/\/(www\.)?youtube\.com\/watch\?v=.+"


class MusicJob(Base):
    __tablename__ = "music_jobs"
    id = Column(String, primary_key=True)
    user_email = Column(
        ForeignKey(
            User.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="music_jobs_user_email_fkey",
        ),
        nullable=False,
    )
    artwork_url = Column(String, nullable=True)
    artwork_filename = Column(String, nullable=True)
    original_filename = Column(String, nullable=True)
    filename_url = Column(String, nullable=True)
    youtube_url = Column(String, nullable=True)
    download_filename = Column(String, nullable=True)
    download_url = Column(String, nullable=True)
    title = Column(String, nullable=False)
    artist = Column(String, nullable=False)
    album = Column(String, nullable=False)
    grouping = Column(String, nullable=True)
    completed = Column(Boolean, nullable=False)
    failed = Column(Boolean, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=get_current_time,
    )
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)
