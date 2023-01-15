import math
from fastapi import Path, APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func

from dripdrop.dependencies import AsyncSession, create_db_session

from .dependencies import get_google_user
from .models import YoutubeSubscription, YoutubeChannel, GoogleAccount
from .responses import SubscriptionsResponse, ErrorMessages

subscriptions_api = APIRouter(
    prefix="/subscriptions",
    tags=["YouTube Subscriptions"],
    dependencies=[Depends(get_google_user)],
)


@subscriptions_api.get(
    "/{page}/{per_page}",
    response_model=SubscriptionsResponse,
)
async def get_youtube_subscriptions(
    page: int = Path(..., ge=1),
    per_page: int = Path(..., le=50),
    google_account: GoogleAccount = Depends(get_google_user),
    db: AsyncSession = Depends(create_db_session),
):
    subscription_query = (
        select(YoutubeSubscription)
        .where(YoutubeSubscription.email == google_account.email)
        .alias(name=YoutubeSubscription.__tablename__)
    )
    query = (
        select(
            subscription_query,
            YoutubeChannel.title.label("channel_title"),
            YoutubeChannel.thumbnail.label("channel_thumbnail"),
        )
        .select_from(
            subscription_query.join(
                YoutubeChannel,
                YoutubeChannel.id == YoutubeSubscription.channel_id,
            )
        )
        .order_by(YoutubeChannel.title)
    )
    results = await db.execute(query.offset((page - 1) * per_page))
    subscriptions: list[YoutubeSubscription] = results.mappings().fetchmany(per_page)
    count: int = await db.scalar(select(func.count(query.subquery().columns.id)))
    total_pages = math.ceil(count / per_page)
    if page > total_pages:
        raise HTTPException(
            detail=ErrorMessages.PAGE_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
        )
    return SubscriptionsResponse(subscriptions=subscriptions, total_pages=total_pages)
