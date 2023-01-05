from fastapi import FastAPI, Depends, Response, status

from dripdrop.services.cron import cron_service

from .dependencies import get_admin_user


app = FastAPI(openapi_tags=["Admin"])


@app.get(
    "/cron/run",
    dependencies=[Depends(get_admin_user)],
    responses={status.HTTP_403_FORBIDDEN: {"description": "Not an admin user"}},
)
async def run_cronjobs():
    await cron_service.async_run_cron_jobs()
    return Response(None, status_code=status.HTTP_200_OK)
