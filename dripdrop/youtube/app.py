from fastapi import Depends, FastAPI, status

from dripdrop.authentication.dependencies import get_authenticated_user
from dripdrop.youtube import channel, subscriptions, video, videos

app = FastAPI(
    openapi_tags=["YouTube"],
    dependencies=[Depends(get_authenticated_user)],
    responses={status.HTTP_403_FORBIDDEN: {}},
)
app.include_router(channel.api)
app.include_router(subscriptions.api)
app.include_router(video.api)
app.include_router(videos.api)
