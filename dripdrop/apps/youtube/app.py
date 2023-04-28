from fastapi import Depends, FastAPI, status

from dripdrop.apps.authentication.dependencies import get_authenticated_user

from .channels import channels_api
from .subscriptions import subscriptions_api
from .videos import videos_api

app = FastAPI(
    openapi_tags=["YouTube"],
    dependencies=[Depends(get_authenticated_user)],
    responses={status.HTTP_403_FORBIDDEN: {}},
)
app.include_router(videos_api)
app.include_router(subscriptions_api)
app.include_router(channels_api)
