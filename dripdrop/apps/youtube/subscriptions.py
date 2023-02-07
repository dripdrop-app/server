import math
from fastapi import Path, APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func

from dripdrop.dependencies import AsyncSession, create_db_session

from .dependencies import get_google_account
from .models import YoutubeSubscription, YoutubeChannel, GoogleAccount
from .responses import SubscriptionsResponse, ErrorMessages

subscriptions_api = APIRouter(
    prefix="/subscriptions",
    tags=["YouTube Subscriptions"],
    dependencies=[Depends(get_google_account)],
)


@subscriptions_api.get(
    "/{page}/{per_page}",
    response_model=SubscriptionsResponse,
)
async def get_youtube_subscriptions(
    page: int = Path(..., ge=1),
    per_page: int = Path(..., le=50),
    google_account: GoogleAccount = Depends(get_google_account),
    session: AsyncSession = Depends(create_db_session),
):
    subscription_query = (
        select(YoutubeSubscription)
        .where(YoutubeSubscription.email == google_account.email)
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
