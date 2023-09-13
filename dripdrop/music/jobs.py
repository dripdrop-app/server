import math
from fastapi import (
    APIRouter,
    Depends,
    Path,
    WebSocket,
    HTTPException,
    status,
)
from sqlalchemy import select, func

from dripdrop.authentication.dependencies import (
    AuthenticatedUser,
    get_authenticated_user,
)
from dripdrop.base.dependencies import DatabaseSession
from dripdrop.music.models import MusicJob
from dripdrop.music.responses import (
    MusicJobUpdateResponse,
    MusicJobsResponse,
    ErrorMessages,
)
from dripdrop.services import database
from dripdrop.services.websocket_channel import (
    RedisChannels,
    WebsocketChannel,
)


api = APIRouter(
    prefix="/jobs",
    tags=["Music Jobs"],
    dependencies=[Depends(get_authenticated_user)],
)


@api.get(
    "/{page}/{per_page}",
    response_model=MusicJobsResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": ErrorMessages.PAGE_NOT_FOUND}
    },
)
async def get_jobs(
    user: AuthenticatedUser,
    session: DatabaseSession,
    page: int = Path(..., ge=1),
    per_page: int = Path(..., le=50, gt=0),
):
    query = (
        select(MusicJob)
        .where(MusicJob.user_email == user.email, MusicJob.deleted_at.is_(None))
        .order_by(MusicJob.created_at.desc())
    )
    results = await session.scalars(query.offset((page - 1) * per_page).limit(per_page))
    music_jobs = list(map(lambda job: job, results.all()))
    count_query = select(func.count(query.subquery().columns.id))
    count = await session.scalar(count_query)
    total_pages = math.ceil(count / per_page)
    if page > total_pages and page != 1:
        raise HTTPException(
            detail=ErrorMessages.PAGE_NOT_FOUND, status_code=status.HTTP_404_NOT_FOUND
        )
    return MusicJobsResponse(music_jobs=music_jobs, total_pages=total_pages)


@api.websocket("/listen")
async def listen_jobs(user: AuthenticatedUser, websocket: WebSocket):
    async def handler(msg):
        message = MusicJobUpdateResponse.model_validate(msg)
        job_id = message.id
        async with database.create_session() as session:
            query = select(MusicJob).where(
                MusicJob.user_email == user.email,
                MusicJob.id == job_id,
                MusicJob.deleted_at.is_(None),
            )
            results = await session.scalars(query)
            music_job = results.first()
            if music_job:
                await websocket.send_json(message.model_dump())

    await WebsocketChannel(channel=RedisChannels.MUSIC_JOB_UPDATE).listen(
        websocket=websocket, handler=handler
    )
