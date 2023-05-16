from sqlalchemy import select

from dripdrop.authentication.models import User
from dripdrop.services.database import AsyncSession
from dripdrop.youtube.models import (
    YoutubeChannel,
    YoutubeVideo,
    YoutubeVideoCategory,
    YoutubeVideoLike,
    YoutubeVideoQueue,
    YoutubeVideoWatch,
)
from dripdrop.youtube.responses import YoutubeVideoResponse


async def get_videos_attributes(
    session: AsyncSession, user: User, videos: list[YoutubeVideo]
):
    video_ids = [video.id for video in videos]
    channel_ids = {video.channel_id for video in videos}
    category_ids = {video.category_id for video in videos}

    query = select(YoutubeChannel).where(YoutubeChannel.id.in_(channel_ids))
    results = await session.scalars(query)
    channels = {channel.id: channel for channel in results.all()}

    query = select(YoutubeVideoCategory).where(
        YoutubeVideoCategory.id.in_(category_ids)
    )
    results = await session.scalars(query)
    categories = {category.id: category for category in results.all()}

    query = select(YoutubeVideoWatch).where(
        YoutubeVideoWatch.video_id.in_(video_ids), YoutubeVideoWatch.email == user.email
    )
    results = await session.scalars(query)
    watches = {watch.video_id: watch for watch in results.all()}

    query = select(YoutubeVideoQueue).where(
        YoutubeVideoQueue.video_id.in_(video_ids), YoutubeVideoQueue.email == user.email
    )
    results = await session.scalars(query)
    queues = {queue.video_id: queue for queue in results.all()}

    query = select(YoutubeVideoLike).where(
        YoutubeVideoLike.video_id.in_(video_ids), YoutubeVideoLike.email == user.email
    )
    results = await session.scalars(query)
    likes = {like.video_id: like for like in results.all()}

    video_responses: list[YoutubeVideoResponse] = []

    for video in videos:
        channel = channels[video.channel_id]
        category = categories[video.category_id]
        watch = watches.get(video.id)
        like = likes.get(video.id)
        queue = queues.get(video.id)
        video_responses.append(
            YoutubeVideoResponse(
                **video.__dict__,
                channel_title=channel.title,
                channel_thumbnail=channel.thumbnail,
                category_name=category.name,
                watched=watch.created_at if watch else None,
                liked=like.created_at if like else None,
                queued=queue.created_at if queue else None
            )
        )

    return video_responses
