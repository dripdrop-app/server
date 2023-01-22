from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy import select

from dripdrop.dependencies import AsyncSession, create_db_session

from .dependencies import get_google_user
from .models import YoutubeChannel
from .responses import YoutubeChannelResponse, ErrorMessages

channels_api = APIRouter(
    prefix="/channels",
    tags=["YouTube Channels"],
    dependencies=[Depends(get_google_user)],
)


@channels_api.get(
    "",
    response_model=YoutubeChannelResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": ErrorMessages.CHANNEL_NOT_FOUND}
    },
)
async def get_youtube_channel(
    channel_id: str = Query(...), session: AsyncSession = Depends(create_db_session)
):
    query = select(YoutubeChannel).where(YoutubeChannel.id == channel_id)
    results = await session.scalars(query)
    channel: YoutubeChannel | None = results.first()
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages.CHANNEL_NOT_FOUND,
        )
    return YoutubeChannelResponse(
        id=channel.id, title=channel.title, thumbnail=channel.thumbnail
    )
