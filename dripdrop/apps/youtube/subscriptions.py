import math
import uuid
from datetime import datetime
from fastapi import Path, APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy import select, func

from dripdrop.dependencies import (
    AsyncSession,
    create_db_session,
    get_authenticated_user,
    User,
)
from dripdrop.settings import settings

from .models import YoutubeSubscription, YoutubeChannel
from .responses import SubscriptionsResponse, ErrorMessages

subscriptions_api = APIRouter(
    prefix="/subscriptions",
    tags=["YouTube Subscriptions"],
    dependencies=[Depends(get_authenticated_user)],
)


@subscriptions_api.get(
    "/{page}/{per_page}",
    response_model=SubscriptionsResponse,
)
async def get_youtube_subscriptions(
    page: int = Path(..., ge=1),
    per_page: int = Path(..., le=50),
    user: User = Depends(get_authenticated_user),
    session: AsyncSession = Depends(create_db_session),
):
    subscription_query = (
        select(YoutubeSubscription)
        .where(YoutubeSubscription.email == user.email)
        .subquery()
    )
    query = (
        select(
            subscription_query.columns.channel_id,
            YoutubeChannel.title.label("channel_title"),
            YoutubeChannel.thumbnail.label("channel_thumbnail"),
            subscription_query.columns.published_at,
        )
        .select_from(
            subscription_query.join(
                YoutubeChannel,
                YoutubeChannel.id == subscription_query.columns.channel_id,
            )
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
    "/add",
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
    query = select(YoutubeSubscription).where(
        YoutubeSubscription.email == user.email,
        YoutubeSubscription.channel_id == channel_id,
    )
    results = await session.scalars(query)
    subscription = results.first()
    if subscription:
        raise HTTPException(
            detail=ErrorMessages.SUBSCRIPTION_ALREADY_EXIST,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    session.add(
        YoutubeSubscription(
            id=str(uuid.uuid4()),
            email=user.email,
            channel_id=channel_id,
            published_at=datetime.now(settings.timezone),
        )
    )
    await session.commit()
    return Response(None, status_code=status.HTTP_201_CREATED)
