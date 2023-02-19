from fastapi import FastAPI, Depends, Response, status, Query
from pydantic import EmailStr

from dripdrop.apps.music.tasks import music_tasker
from dripdrop.apps.youtube.tasks import youtube_tasker
from dripdrop.rq import enqueue
from dripdrop.services.cron import cron_service

from .dependencies import get_admin_user


app = FastAPI(
    openapi_tags=["Admin"],
    dependencies=[Depends(get_admin_user)],
)


@app.get(
    "/cron/run",
    responses={status.HTTP_403_FORBIDDEN: {}},
)
async def run_cron_jobs():
    await cron_service.run_cron_jobs()
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


@app.get("/update_channels/meta")
async def run_update_channels_meta():
    await enqueue(function=youtube_tasker.update_channels_meta)
    return Response(None, status_code=status.HTTP_200_OK)


@app.get("/update_channels/video")
async def run_update_channels_videos():
    await enqueue(function=youtube_tasker.update_channels_videos)
    return Response(None, status_code=status.HTTP_200_OK)


@app.get("/update_video_categories")
def run_update_video_categories():
    enqueue(function=youtube_tasker.update_video_categories)
    return Response(None, status_code=status.HTTP_200_OK)
