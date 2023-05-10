from fastapi import Depends, FastAPI, status

from dripdrop.authentication.dependencies import get_authenticated_user
from dripdrop.youtube import channels, subscriptions, videos

app = FastAPI(
    openapi_tags=["YouTube"],
    dependencies=[Depends(get_authenticated_user)],
    responses={status.HTTP_403_FORBIDDEN: {}},
)
app.include_router(channels.api)
app.include_router(subscriptions.api)
app.include_router(videos.api)
