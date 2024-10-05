import asyncio
from fastapi import FastAPI, Depends, Response, status, Query
from pydantic import EmailStr
from typing import Optional

from dripdrop.authentication.dependencies import get_admin_user
from dripdrop.music import tasks as music_tasks
from dripdrop.services import rq_client
from dripdrop.youtube import tasks as youtube_tasks

app = FastAPI(
    openapi_tags=["Admin"],
    dependencies=[Depends(get_admin_user)],
    responses={status.HTTP_403_FORBIDDEN: {}},
)


@app.get("/session")
async def check_admin_session():
    return Response(None, status_code=status.HTTP_200_OK)


@app.get("/cron/run")
async def run_cron_jobs():
    update_video_categories_job = await asyncio.to_thread(
        rq_client.default.enqueue, youtube_tasks.update_video_categories
    )
    update_subscriptions_job = await asyncio.to_thread(
        rq_client.default.enqueue,
        youtube_tasks.update_subscriptions,
        depends_on=update_video_categories_job,
    )
    await asyncio.to_thread(
        rq_client.default.enqueue,
        youtube_tasks.update_channel_videos,
        depends_on=update_subscriptions_job,
    )
    await asyncio.to_thread(
        rq_client.default.enqueue, music_tasks.delete_old_music_jobs
    )
    return Response(None, status_code=status.HTTP_200_OK)


@app.get("/delete_old_jobs")
async def run_delete_old_jobs():
    await asyncio.to_thread(
        rq_client.default.enqueue, music_tasks.delete_old_music_jobs
    )
    return Response(None, status_code=status.HTTP_200_OK)


@app.get("/update_subscriptions")
async def run_update_subscriptions(email: EmailStr | None = Query(None)):
    if email:
        await asyncio.to_thread(
            rq_client.default.enqueue,
            youtube_tasks.update_user_subscriptions,
            email=email,
        )
    else:
        await asyncio.to_thread(
            rq_client.default.enqueue, youtube_tasks.update_subscriptions
        )
    return Response(None, status_code=status.HTTP_200_OK)


@app.get("/update_channel_videos")
async def run_update_channel_videos(
    channel_id: Optional[str] = Query(None),
    date_after: Optional[str] = Query(
        None, description="date string with format YYYYMMDD"
    ),
):
    if not channel_id:
        await asyncio.to_thread(
            rq_client.default.enqueue,
            youtube_tasks.update_channel_videos,
            date_after=date_after,
        )
    else:
        await asyncio.to_thread(
            rq_client.default.enqueue,
            youtube_tasks.add_channel_videos,
            channel_id=channel_id,
            date_after=date_after,
        )
    return Response(None, status_code=status.HTTP_200_OK)


@app.get("/update_video_categories")
async def run_update_video_categories():
    await asyncio.to_thread(
        rq_client.default.enqueue, youtube_tasks.update_video_categories
    )
    return Response(None, status_code=status.HTTP_200_OK)
