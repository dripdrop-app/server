from fastapi import Path, APIRouter, Depends
from server.dependencies import (
    GoogleAccount,
    get_google_user,
    DBSession,
    create_db_session,
)
from server.models.api import YoutubeResponses
from server.models.orm import YoutubeSubscriptions, YoutubeChannels
from sqlalchemy import select

youtube_subscriptions_api = APIRouter(
    prefix="/subscriptions",
    tags=["YouTube Subscriptions"],
    dependencies=[Depends(get_google_user)],
)


@youtube_subscriptions_api.get(
    "/{page}/{per_page}",
    response_model=YoutubeResponses.Subscriptions,
)
async def get_youtube_subscriptions(
    page: int = Path(..., ge=1),
    per_page: int = Path(..., le=50),
    google_account: GoogleAccount = Depends(get_google_user),
    db: DBSession = Depends(create_db_session),
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
        .offset((page - 1) * per_page)
    )
    results = await db.execute(query)
    subscriptions = results.mappings().fetchmany(per_page)
    return YoutubeResponses.Subscriptions(subscriptions=subscriptions).dict(
        by_alias=True
    )
