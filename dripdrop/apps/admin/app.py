from fastapi import FastAPI, Depends, Response, status, Query
from pydantic import EmailStr

from dripdrop.apps.music.tasks import music_tasker
from dripdrop.apps.youtube.tasks import youtube_tasker
from dripdrop.rq import queue
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
def run_cron_jobs():
    cron_service.run_cron_jobs()
    return Response(None, status_code=status.HTTP_200_OK)


@app.get("/delete_old_jobs")
def run_delete_old_jobs():
    queue.enqueue(music_tasker.delete_old_jobs)
    return Response(None, status_code=status.HTTP_200_OK)


@app.get("/update_subscriptions")
def run_update_subscriptions(email: EmailStr | None = Query(None)):
    job = queue.enqueue(youtube_tasker.update_video_categories, args=(False,))
    if email:
        queue.enqueue(
            youtube_tasker.update_user_subscriptions,
            args=(email,),
            depends_on=job,
        )
    else:
        queue.enqueue(
            youtube_tasker.update_subscriptions,
            depends_on=job,
        )
    return Response(None, status_code=status.HTTP_200_OK)


@app.get("/delete_old_channels")
def run_delete_old_channels():
    queue.enqueue(youtube_tasker.delete_old_channels)
    return Response(None, status_code=status.HTTP_200_OK)


@app.get("/update_channels/meta")
def run_update_channels_meta():
    queue.enqueue(youtube_tasker.update_channels_meta)
    return Response(None, status_code=status.HTTP_200_OK)


@app.get("/update_channels/video")
def run_update_channels_videos():
    queue.enqueue(youtube_tasker.update_channels_videos)
    return Response(None, status_code=status.HTTP_200_OK)


@app.get("/update_video_categories")
def run_update_video_categories():
    queue.enqueue(youtube_tasker.update_video_categories)
    return Response(None, status_code=status.HTTP_200_OK)
