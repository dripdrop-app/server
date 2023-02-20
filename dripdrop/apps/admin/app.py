from fastapi import FastAPI, Depends, Response, status, Query
from pydantic import EmailStr
from typing import Optional

from dripdrop.apps.music.tasks import music_tasker
from dripdrop.apps.youtube.tasks import youtube_tasker
from dripdrop.rq import enqueue
from dripdrop.services.cron import cron

from .dependencies import get_admin_user


app = FastAPI(
    openapi_tags=["Admin"],
    dependencies=[Depends(get_admin_user)],
)


@app.get("/cron/run", responses={status.HTTP_403_FORBIDDEN: {}})
async def run_cron_jobs():
    await cron.run_cron_jobs()
    return Response(None, status_code=status.HTTP_200_OK)


@app.get("/delete_old_jobs")
async def run_delete_old_jobs():
    await enqueue(function=music_tasker.delete_old_jobs)
    return Response(None, status_code=status.HTTP_200_OK)


@app.get("/update_subscriptions")
async def run_update_subscriptions(email: EmailStr | None = Query(None)):
    job = await enqueue(function=youtube_tasker.update_video_categories, args=(False,))
    if email:
        await enqueue(
            function=youtube_tasker.update_user_subscriptions,
            args=(email,),
            depends_on=job,
        )
    else:
        await enqueue(
            function=youtube_tasker.update_subscriptions,
            depends_on=job,
        )
    return Response(None, status_code=status.HTTP_200_OK)


@app.get("/delete_old_channels")
async def run_delete_old_channels():
    await enqueue(function=youtube_tasker.delete_old_channels)
    return Response(None, status_code=status.HTTP_200_OK)


@app.get("/update_channel_videos")
async def run_update_channel_videos(
    channel_id: Optional[str] = Query(None), date_after: Optional[str] = Query(None)
):
    if not channel_id:
        await enqueue(
            function=youtube_tasker.update_channel_videos,
            kwargs={"date_after": date_after},
        )
    else:
        await enqueue(
            function=youtube_tasker.add_new_channel_videos_job,
            kwargs={"channel_id": channel_id, "date_after": date_after},
        )
    return Response(None, status_code=status.HTTP_200_OK)


@app.get("/update_video_categories")
def run_update_video_categories():
    enqueue(function=youtube_tasker.update_video_categories)
    return Response(None, status_code=status.HTTP_200_OK)
