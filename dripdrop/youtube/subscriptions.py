import math
from .dependencies import get_google_user
from .models import YoutubeSubscriptions, YoutubeChannels, GoogleAccount
from .responses import SubscriptionsResponse
from fastapi import Path, APIRouter, Depends
from dripdrop.dependencies import AsyncSession, create_db_session
from sqlalchemy import select, func

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
        select(YoutubeSubscriptions)
        .where(YoutubeSubscriptions.email == google_account.email)
        .alias(name=YoutubeSubscriptions.__tablename__)
    )
    query = (
        select(
            subscription_query,
            YoutubeChannels.title.label("channel_title"),
            YoutubeChannels.thumbnail.label("channel_thumbnail"),
        )
        .select_from(
            subscription_query.join(
                YoutubeChannels,
                YoutubeChannels.id == YoutubeSubscriptions.channel_id,
            )
        )
        .order_by(YoutubeChannels.title)
    )
    results = await db.execute(query.offset((page - 1) * per_page))
    subscriptions = results.mappings().fetchmany(per_page)
    count = await db.scalar(select(func.count(query.c.id)))
    total_pages = math.ceil(count / per_page)
    return SubscriptionsResponse(
        subscriptions=subscriptions, total_pages=total_pages
    ).dict(by_alias=True)
