from fastapi import FastAPI, Response, Depends
from server.dependencies import get_admin_user
from server.elasticsearch import (
    populate_youtube_subscriptions_index,
    populate_youtube_videos_index,
)

app = FastAPI(dependencies=[Depends(get_admin_user)], responses={401: {}})


@app.get("/youtube_videos")
async def index_youtube_videos():
    await populate_youtube_videos_index()
    return Response(None)


@app.get("/youtube_subscriptions")
async def index_youtube_subscriptions():
    await populate_youtube_subscriptions_index()
    return Response(None)
