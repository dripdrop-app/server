from fastapi import APIRouter, HTTPException, Depends, Query, status, Body, Response
from sqlalchemy import select, and_

import dripdrop.utils as dripdrop_utils
from dripdrop.dependencies import (
    AsyncSession,
    create_db_session,
    get_authenticated_user,
    User,
)
from dripdrop.services import rq, scraper

from . import tasks
from .models import YoutubeChannel, YoutubeUserChannel, YoutubeSubscription
from .responses import YoutubeChannelResponse, YoutubeUserChannelResponse, ErrorMessages

channels_api = APIRouter(
    prefix="/channels",
    tags=["YouTube Channels"],
    dependencies=[Depends(get_authenticated_user)],
)


@channels_api.get(
    "", response_model=YoutubeChannelResponse, responses={status.HTTP_404_NOT_FOUND: {}}
)
async def get_youtube_channel(
    channel_id: str = Query(...),
    user: User = Depends(get_authenticated_user),
    session: AsyncSession = Depends(create_db_session),
):
    query = (
        select(
            YoutubeChannel.id,
            YoutubeChannel.title,
            YoutubeChannel.thumbnail,
            YoutubeSubscription.channel_id.label("subscribed"),
        )
        .join(
            YoutubeSubscription,
            and_(
                YoutubeChannel.id == YoutubeSubscription.channel_id,
                YoutubeSubscription.email == user.email,
                YoutubeSubscription.deleted_at.is_(None),
            ),
            isouter=True,
        )
        .where(YoutubeChannel.id == channel_id)
    )
    results = await session.execute(query)
    channel = results.mappings().first()
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages.CHANNEL_NOT_FOUND,
        )
    return YoutubeChannelResponse(
        id=channel.id,
        title=channel.title,
        thumbnail=channel.thumbnail,
        subscribed=bool(channel.subscribed),
    )


@channels_api.get(
    "/user",
    response_model=YoutubeUserChannelResponse,
    responses={status.HTTP_404_NOT_FOUND: {}},
)
async def get_user_youtube_channel(
    user: User = Depends(get_authenticated_user),
    session: AsyncSession = Depends(create_db_session),
):
    query = select(YoutubeUserChannel).where(YoutubeUserChannel.email == user.email)
    results = await session.scalars(query)
    user_channel = results.first()
    if not user_channel:
        raise HTTPException(
            detail=ErrorMessages.CHANNEL_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return YoutubeUserChannelResponse(id=user_channel.id)


@channels_api.post("/user", responses={status.HTTP_400_BAD_REQUEST: {}})
async def update_user_youtube_channel(
    channel_id: str = Body(..., embed=True),
    user: User = Depends(get_authenticated_user),
    session: AsyncSession = Depends(create_db_session),
):
    channel_info = await scraper.get_channel_info(channel_id=channel_id)
    if not channel_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessages.CHANNEL_NOT_FOUND,
        )
    query = select(YoutubeUserChannel).where(YoutubeUserChannel.email == user.email)
    results = await session.scalars(query)
    user_channel = results.first()
    if user_channel:
        current_time = dripdrop_utils.get_current_time()
        time_elasped = current_time - user_channel.modified_at
        if time_elasped.days < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorMessages.WAIT_TO_UPDATE_CHANNEL,
            )
        user_channel.id = channel_info.id
    else:
        session.add(YoutubeUserChannel(id=channel_info.id, email=user.email))
    await session.commit()
    await rq.enqueue(
        tasks.update_user_subscriptions,
        kwargs={"email": user.email},
        retry=rq.Retry(max=2),
    )
    return Response(None, status_code=status.HTTP_200_OK)
