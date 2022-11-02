from .base_model import Base
from .users import Users
from sqlalchemy import (
    Column,
    String,
    text,
    TIMESTAMP,
    ForeignKey,
    Boolean,
    Integer,
)
from sqlalchemy.orm import relationship


class GoogleAccounts(Base):
    __tablename__ = "google_accounts"

    email = Column(String, primary_key=True)
    user_email = Column(
        ForeignKey(
            Users.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="google_accounts_user_email_fkey",
        ),
        nullable=False,
        unique=True,
    )
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=False)
    expires = Column(Integer, nullable=False)
    subscriptions_loading = Column(
        Boolean,
        nullable=False,
        server_default="0",
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )
    last_updated = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
        server_onupdate=text("NOW()"),
    )
    user = relationship(
        "Users",
        back_populates="google_account",
        uselist=False,
    )
    subscriptions = relationship(
        "YoutubeSubscriptions",
        back_populates="google_account",
    )
    likes = relationship("YoutubeVideoLikes", back_populates="google_account")
    queues = relationship("YoutubeVideoQueues", back_populates="google_account")
    watches = relationship("YoutubeVideoWatches", back_populates="google_account")
