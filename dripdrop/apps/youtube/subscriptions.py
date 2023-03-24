import math
from datetime import timedelta
from fastapi import Path, APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy import select, func, and_

from dripdrop.dependencies import (
    AsyncSession,
    create_db_session,
    get_authenticated_user,
    User,
)
from dripdrop.services import rq, scraper
from dripdrop.utils import get_current_time

from . import tasks
from .models import YoutubeSubscription, YoutubeChannel
from .responses import SubscriptionsResponse, YoutubeSubscriptionResponse, ErrorMessages

subscriptions_api = APIRouter(
    prefix="/subscriptions",
    tags=["YouTube Subscriptions"],
    dependencies=[Depends(get_authenticated_user)],
)


@subscriptions_api.get(
    "/{page}/{per_page}",
    response_model=SubscriptionsResponse,
    responses={status.HTTP_404_NOT_FOUND: {}},
)
async def get_youtube_subscriptions(
    page: int = Path(..., ge=1),
    per_page: int = Path(..., le=50),
    user: User = Depends(get_authenticated_user),
    session: AsyncSession = Depends(create_db_session),
):
    query = (
        select(
            YoutubeSubscription.channel_id,
            YoutubeChannel.title.label("channel_title"),
            YoutubeChannel.thumbnail.label("channel_thumbnail"),
        )
        .join(
            YoutubeChannel,
            and_(
                YoutubeSubscription.channel_id == YoutubeChannel.id,
                YoutubeSubscription.email == user.email,
            ),
        )
        .where(
            YoutubeSubscription.deleted_at.is_(None),
        )
        .order_by(YoutubeChannel.title)
    )
    results = await session.execute(query.offset((page - 1) * per_page))
    subscriptions = results.mappings().fetchmany(per_page)
    count = await session.scalar(
        select(func.count(query.subquery().columns.channel_id))
    )
    total_pages = math.ceil(count / per_page)
    if page > total_pages and page != 1:
        raise HTTPException(
            detail=ErrorMessages.PAGE_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
        )
    return SubscriptionsResponse(subscriptions=subscriptions, total_pages=total_pages)


@subscriptions_api.put(
    "/user",
    response_model=YoutubeSubscriptionResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": ErrorMessages.SUBSCRIPTION_ALREADY_EXIST
        }
    },
)
async def add_user_subscription(
    channel_id: str = Query(...),
    user: User = Depends(get_authenticated_user),
    session: AsyncSession = Depends(create_db_session),
):
    channel_info = await scraper.get_channel_info(channel_id=channel_id)
    if not channel_info:
        raise HTTPException(
            detail=ErrorMessages.CHANNEL_NOT_FOUND,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    query = select(YoutubeSubscription).where(
        YoutubeSubscription.email == user.email,
        YoutubeSubscription.channel_id == channel_info.id,
    )
    results = await session.scalars(query)
    subscription = results.first()
    query = select(YoutubeChannel).where(YoutubeChannel.id == channel_info.id)
    results = await session.scalars(query)
    channel = results.first()
    if not subscription:
        if not channel:
            channel = YoutubeChannel(
                id=channel_info.id,
                title=channel_info.title,
                thumbnail=channel_info.thumbnail,
                last_videos_updated=get_current_time() - timedelta(days=30),
            )
            session.add(channel)
            await session.commit()
        subscription = YoutubeSubscription(
            email=user.email,
            channel_id=channel_info.id,
            user_submitted=True,
        )
        session.add(subscription)
    else:
        if subscription.deleted_at is None:
            raise HTTPException(
                detail=ErrorMessages.SUBSCRIPTION_ALREADY_EXIST,
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        subscription.deleted_at = None
    await session.commit()
    await rq.enqueue(
        tasks.add_new_channel_videos_job, kwargs={"channel_id": channel.id}
    )
    return YoutubeSubscriptionResponse(
        channel_id=subscription.channel_id,
        channel_title=channel.title,
        channel_thumbnail=channel.thumbnail,
    )


@subscriptions_api.delete("/user", responses={status.HTTP_404_NOT_FOUND: {}})
async def delete_user_subscription(
    channel_id: str = Query(...),
    user: User = Depends(get_authenticated_user),
    session: AsyncSession = Depends(create_db_session),
):
    query = select(YoutubeSubscription).where(
        YoutubeSubscription.email == user.email,
        YoutubeSubscription.channel_id == channel_id,
    )
    results = await session.scalars(query)
    subscription = results.first()
    if not subscription:
        raise HTTPException(
            detail=ErrorMessages.SUBSCRIPTION_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )
    subscription.deleted_at = get_current_time()
    await session.commit()
    return Response(None, status_code=status.HTTP_200_OK)
