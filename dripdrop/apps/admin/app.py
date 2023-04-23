import asyncio
from fastapi import FastAPI, Depends, Response, status, Query
from pydantic import EmailStr
from typing import Optional

from dripdrop.apps.music import tasks as music_tasks
from dripdrop.apps.youtube import tasks as youtube_tasks
from dripdrop.services import cron, rq_client

from . import dependencies


app = FastAPI(
    openapi_tags=["Admin"],
    dependencies=[Depends(dependencies.get_admin_user)],
    responses={status.HTTP_403_FORBIDDEN: {}},
)


@app.get("/session")
async def check_admin_session():
    return Response(None, status_code=status.HTTP_200_OK)


@app.get("/cron/run")
async def run_cron_jobs():
    await cron.run_cron_jobs()
    return Response(None, status_code=status.HTTP_200_OK)


@app.get("/delete_old_jobs")
async def run_delete_old_jobs():
    await asyncio.to_thread(rq_client.queue.enqueue, music_tasks.delete_old_music_jobs)
    return Response(None, status_code=status.HTTP_200_OK)


@app.get("/update_subscriptions")
async def run_update_subscriptions(email: EmailStr | None = Query(None)):
    if email:
        await asyncio.to_thread(
            rq_client.queue.enqueue,
            youtube_tasks.update_user_subscriptions,
            email=email,
        )
    else:
        await asyncio.to_thread(
            rq_client.queue.enqueue, youtube_tasks.update_subscriptions
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
            rq_client.queue.enqueue,
            youtube_tasks.update_channel_videos,
            date_after=date_after,
        )
    else:
        await asyncio.to_thread(
            rq_client.queue.enqueue,
            youtube_tasks.add_channel_videos,
            channel_id=channel_id,
            date_after=date_after,
        )
    return Response(None, status_code=status.HTTP_200_OK)
