import asyncio
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Body,
    Response,
    WebSocket,
    Path,
)
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, and_

import dripdrop.utils as dripdrop_utils
from dripdrop.authentication.dependencies import (
    AuthenticatedUser,
    get_authenticated_user,
)
from dripdrop.base.dependencies import DatabaseSession
from dripdrop.services import rq_client, scraper
from dripdrop.services.websocket_channel import WebsocketChannel, RedisChannels
from dripdrop.youtube import tasks
from dripdrop.youtube.models import (
    YoutubeChannel,
    YoutubeUserChannel,
    YoutubeSubscription,
)
from dripdrop.youtube.responses import (
    YoutubeChannelResponse,
    YoutubeChannelUpdateResponse,
    YoutubeUserChannelResponse,
    ErrorMessages,
)


api = APIRouter(
    prefix="/channel",
    tags=["YouTube Channel"],
    dependencies=[Depends(get_authenticated_user)],
)


@api.websocket("/listen")
async def listen_channels(websocket: WebSocket):
    async def handler(msg):
        await websocket.send_json(
            jsonable_encoder(YoutubeChannelUpdateResponse.parse_obj(msg).dict())
        )

    await WebsocketChannel(channel=RedisChannels.YOUTUBE_CHANNEL_UPDATE).listen(
        websocket=websocket, handler=handler
    )


@api.get(
    "/user",
    response_model=YoutubeUserChannelResponse,
    responses={status.HTTP_404_NOT_FOUND: {}},
)
async def get_user_youtube_channel(user: AuthenticatedUser, session: DatabaseSession):
    query = select(YoutubeUserChannel).where(YoutubeUserChannel.email == user.email)
    results = await session.scalars(query)
    user_channel = results.first()
    if not user_channel:
        raise HTTPException(
            detail=ErrorMessages.CHANNEL_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return YoutubeUserChannelResponse(id=user_channel.id)


@api.post("/user", responses={status.HTTP_400_BAD_REQUEST: {}})
async def update_user_youtube_channel(
    user: AuthenticatedUser,
    session: DatabaseSession,
    channel_id: str = Body(..., embed=True),
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
        rq_client.default.enqueue, tasks.update_user_subscriptions, email=user.email
    )
    return Response(None, status_code=status.HTTP_200_OK)


@api.get(
    "/{channel_id}",
    response_model=YoutubeChannelResponse,
    responses={status.HTTP_404_NOT_FOUND: {}},
)
async def get_youtube_channel(
    user: AuthenticatedUser, session: DatabaseSession, channel_id: str = Path(...)
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
