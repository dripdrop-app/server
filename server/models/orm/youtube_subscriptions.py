from .base_model import Base
from .google_accounts import GoogleAccounts
from .youtube_channels import YoutubeChannels
from sqlalchemy import Column, String, text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship


class YoutubeSubscriptions(Base):
    __tablename__ = "youtube_subscriptions"
    id = Column(String, primary_key=True)
    channel_id = Column(
        ForeignKey(
            YoutubeChannels.id,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_subscriptions_channel_id_fkey",
        ),
        nullable=False,
    )
    email = Column(
        ForeignKey(
            GoogleAccounts.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="youtube_subscriptions_email_fkey",
        ),
        nullable=False,
    )
    published_at = Column(TIMESTAMP(timezone=True), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )
    channel = relationship("YoutubeChannels", back_populates="subscriptions")
    google_account = relationship("GoogleAccounts", back_populates="subscriptions")
