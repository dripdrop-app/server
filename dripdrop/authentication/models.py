from typing import TYPE_CHECKING

from passlib.context import CryptContext
from sqlalchemy import event, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dripdrop.base.models import Base
from dripdrop.services.database import AsyncSession

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

if TYPE_CHECKING:
    from dripdrop.music.models import MusicJob
    from dripdrop.youtube.models import (
        YoutubeSubscription,
        YoutubeUserChannel,
        YoutubeVideoLike,
        YoutubeVideoQueue,
        YoutubeVideoWatch,
    )


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(primary_key=True)
    password: Mapped[str] = mapped_column(nullable=False)
    admin: Mapped[bool] = mapped_column(nullable=False, default=False)
    verified: Mapped[bool] = mapped_column(nullable=False, default=False)
    jobs: Mapped[list["MusicJob"]] = relationship("MusicJob", back_populates="user")
    youtube_channels: Mapped[list["YoutubeUserChannel"]] = relationship(
        "YoutubeUserChannel", back_populates="user"
    )
    youtube_subscriptions: Mapped[list["YoutubeSubscription"]] = relationship(
        "YoutubeSubscription", back_populates="user"
    )
    youtube_video_queues: Mapped[list["YoutubeVideoQueue"]] = relationship(
        "YoutubeVideoQueue", back_populates="user"
    )
    youtube_video_likes: Mapped[list["YoutubeVideoLike"]] = relationship(
        "YoutubeVideoLike", back_populates="user"
    )
    youtube_video_watches: Mapped[list["YoutubeVideoWatch"]] = relationship(
        "YoutubeVideoWatch", back_populates="user"
    )

    @classmethod
    async def find_by_email(cls, email: str, session: AsyncSession):
        query = select(User).where(User.email == email)
        user = await session.scalar(query)
        return user


@event.listens_for(User, "init")
def init_user(target: User, args, kwargs):
    if "password" in kwargs:
        kwargs["password"] = password_context.hash(kwargs["password"])
