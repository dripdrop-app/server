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
from sqlalchemy import select
from sqlalchemy.orm import joinedload

import dripdrop.utils as dripdrop_utils
from dripdrop.authentication.dependencies import (
    AuthenticatedUser,
    get_authenticated_user,
)
from dripdrop.base.dependencies import DatabaseSession
from dripdrop.services import google_api, rq_client
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
            YoutubeChannelUpdateResponse.model_validate_json(msg).model_dump()
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
    user_channel = await session.scalar(query)
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
    channel_info = await google_api.get_channel_info(channel_id=channel_id)
    if not channel_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessages.CHANNEL_NOT_FOUND,
        )
    query = select(YoutubeUserChannel).where(YoutubeUserChannel.email == user.email)
    user_channel = await session.scalar(query)
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
        select(YoutubeChannel)
        .where(YoutubeChannel.id == channel_id)
        .options(
            joinedload(
                YoutubeChannel.subscriptions.and_(
                    YoutubeSubscription.email == user.email,
                    YoutubeSubscription.deleted_at.is_(None),
                )
            )
        )
    )
    results = await session.execute(query)
    channel = results.scalar()
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorMessages.CHANNEL_NOT_FOUND,
        )
    return YoutubeChannelResponse(
        id=channel.id,
        title=channel.title,
        thumbnail=channel.thumbnail,
        subscribed=bool(channel.subscriptions[0] if channel.subscriptions else False),
        updating=channel.updating,
    )
