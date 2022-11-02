from fastapi import APIRouter, HTTPException, Depends, Query
from server.dependencies import DBSession, create_db_session, get_google_user
from server.models.api import YoutubeChannel
from server.models.orm import YoutubeChannels
from sqlalchemy import select

youtube_channels_api = APIRouter(
    prefix="/channels",
    tags=["YouTube Channels"],
    dependencies=[Depends(get_google_user)],
)


@youtube_channels_api.get("", response_model=YoutubeChannel)
async def get_youtube_channel(
    channel_id: str = Query(...),
    db: DBSession = Depends(create_db_session),
):
    query = select(YoutubeChannels).where(YoutubeChannels.id == channel_id)
    results = await db.scalars(query)
    channel = results.first()
    if not channel:
        raise HTTPException(404)
    return YoutubeChannel.from_orm(channel).dict(by_alias=True)
