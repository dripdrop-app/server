from fastapi import FastAPI, Depends, Response, status, Query
from pydantic import EmailStr
from typing import Optional

from dripdrop.apps.music.tasks import music_tasker
from dripdrop.apps.youtube.tasks import youtube_tasker
from dripdrop.services import cron, rq

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
    await rq.enqueue(function=music_tasker.delete_old_jobs)
    return Response(None, status_code=status.HTTP_200_OK)


@app.get("/update_subscriptions")
async def run_update_subscriptions(email: EmailStr | None = Query(None)):
    job = await rq.enqueue(
        function=youtube_tasker.update_video_categories, args=(False,)
    )
    if email:
        await rq.enqueue(
            function=youtube_tasker.update_user_subscriptions,
            args=(email,),
            depends_on=job,
        )
    else:
        await rq.enqueue(
            function=youtube_tasker.update_subscriptions,
            depends_on=job,
        )
    return Response(None, status_code=status.HTTP_200_OK)


@app.get("/delete_old_channels")
async def run_delete_old_channels():
    await rq.enqueue(function=youtube_tasker.delete_old_channels)
    return Response(None, status_code=status.HTTP_200_OK)


@app.get("/update_channel_videos")
async def run_update_channel_videos(
    channel_id: Optional[str] = Query(None), date_after: Optional[str] = Query(None)
):
    if not channel_id:
        await rq.enqueue(
            function=youtube_tasker.update_channel_videos,
            kwargs={"date_after": date_after},
        )
    else:
        await rq.enqueue(
            function=youtube_tasker.add_new_channel_videos_job,
            kwargs={"channel_id": channel_id, "date_after": date_after},
        )
    return Response(None, status_code=status.HTTP_200_OK)


@app.get("/update_video_categories")
def run_update_video_categories():
    rq.enqueue(function=youtube_tasker.update_video_categories)
    return Response(None, status_code=status.HTTP_200_OK)
