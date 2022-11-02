from .base_model import Base
from sqlalchemy import Column, String, Boolean, text, TIMESTAMP
from sqlalchemy.orm import relationship


class Users(Base):
    __tablename__ = "users"
    email = Column(String, primary_key=True)
    password = Column(String, nullable=False)
    admin = Column(Boolean, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )
    google_account = relationship(
        "GoogleAccounts",
        back_populates="user",
        uselist=False,
    )
    sessions = relationship("Sessions", back_populates="user")
    music_jobs = relationship("MusicJobs", back_populates="user")
