from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy import select

from dripdrop.dependencies import AsyncSession, create_db_session

from .dependencies import get_google_user
from .models import YoutubeChannel, YoutubeChannels


channels_api = APIRouter(
    prefix="/channels",
    tags=["YouTube Channels"],
    dependencies=[Depends(get_google_user)],
)


@channels_api.get(
    "",
    response_model=YoutubeChannel,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Youtube Channel not found"}},
)
async def get_youtube_channel(
    channel_id: str = Query(...), db: AsyncSession = Depends(create_db_session)
):
    query = select(YoutubeChannels).where(YoutubeChannels.id == channel_id)
    results = await db.scalars(query)
    channel = results.first()
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Youtube Channel not found"
        )
    return YoutubeChannel.from_orm(channel).dict(by_alias=True)
