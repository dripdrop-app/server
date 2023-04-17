import asyncio
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    Query,
    status,
    Body,
    Response,
    WebSocket,
)
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, and_

import dripdrop.utils as dripdrop_utils
from dripdrop.apps.authentication.models import User
from dripdrop.dependencies import create_database_session, get_authenticated_user
from dripdrop.services import rq_client, scraper
from dripdrop.services.database import AsyncSession
from dripdrop.services.websocket_channel import WebsocketChannel, RedisChannels

from . import tasks
from .models import YoutubeChannel, YoutubeUserChannel, YoutubeSubscription
from .responses import (
    YoutubeChannelResponse,
    YoutubeChannelUpdateResponse,
    YoutubeUserChannelResponse,
    ErrorMessages,
)

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
    session: AsyncSession = Depends(create_database_session),
):
    query = (
        select(
            YoutubeChannel.id,
            YoutubeChannel.title,
            YoutubeChannel.thumbnail,
            YoutubeChannel.updating,
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
        updating=channel.updating,
    )


@channels_api.websocket("/listen")
async def listen_channels(websocket: WebSocket):
    async def handler(msg):
        await websocket.send_json(
            jsonable_encoder(YoutubeChannelUpdateResponse.parse_obj(msg).dict())
        )

    await WebsocketChannel(channel=RedisChannels.YOUTUBE_CHANNEL_UPDATE).listen(
        websocket=websocket, handler=handler
    )


@channels_api.get(
    "/user",
    response_model=YoutubeUserChannelResponse,
    responses={status.HTTP_404_NOT_FOUND: {}},
)
async def get_user_youtube_channel(
    user: User = Depends(get_authenticated_user),
    session: AsyncSession = Depends(create_database_session),
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
    session: AsyncSession = Depends(create_database_session),
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
    await asyncio.to_thread(
        rq_client.queue.enqueue, tasks.update_user_subscriptions, email=user.email
    )
    return Response(None, status_code=status.HTTP_200_OK)
