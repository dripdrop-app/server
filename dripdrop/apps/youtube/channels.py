from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query, status, Body, Response
from sqlalchemy import select

from dripdrop.dependencies import (
    AsyncSession,
    create_db_session,
    get_authenticated_user,
    User,
)
from dripdrop.settings import settings

from .models import YoutubeChannel, YoutubeUserChannel
from .responses import YoutubeChannelResponse, YoutubeUserChannelResponse, ErrorMessages

channels_api = APIRouter(
    prefix="/channels",
    tags=["YouTube Channels"],
    dependencies=[Depends(get_authenticated_user)],
)


@channels_api.get(
    "",
    response_model=YoutubeChannelResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": ErrorMessages.CHANNEL_NOT_FOUND}
    },
)
async def get_youtube_channel(
    channel_id: str = Query(...),
    session: AsyncSession = Depends(create_db_session),
):
    query = select(YoutubeChannel).where(YoutubeChannel.id == channel_id)
    results = await session.scalars(query)
    channel = results.first()
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages.CHANNEL_NOT_FOUND,
        )
    return YoutubeChannelResponse(
        id=channel.id, title=channel.title, thumbnail=channel.thumbnail
    )


@channels_api.get("/user")
async def get_user_youtube_channel(
    user: User = Depends(get_authenticated_user),
    session: AsyncSession = Depends(create_db_session),
):
    query = select(YoutubeUserChannel).where(YoutubeUserChannel.email == user.email)
    results = await session.scalars(query)
    user_channel = results.first()
    if not user_channel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return YoutubeUserChannelResponse(id=user_channel.id)


@channels_api.post(
    "/user/update",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": ErrorMessages.WAIT_TO_UPDATE_CHANNEL
        }
    },
)
async def update_user_youtube_channel(
    channel_id: str = Body(..., embed=True),
    user: User = Depends(get_authenticated_user),
    session: AsyncSession = Depends(create_db_session),
):
    query = select(YoutubeUserChannel).where(YoutubeUserChannel.email == user.email)
    results = await session.scalars(query)
    user_channel = results.first()
    if user_channel:
        current_time = datetime.now(settings.timezone)
        time_elasped = current_time - user_channel.modified_at
        if time_elasped.days < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorMessages.WAIT_TO_UPDATE_CHANNEL,
            )
        user_channel.id = channel_id
    else:
        session.add(YoutubeUserChannel(id=channel_id, email=user.email))
    await session.commit()
    return Response(None, status_code=status.HTTP_200_OK)
