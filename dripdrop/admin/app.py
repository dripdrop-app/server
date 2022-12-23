from .dependencies import get_admin_user
from asgiref.sync import sync_to_async
from dripdrop.services.cron import cron_service
from fastapi import FastAPI, Depends, Response, status


app = FastAPI(openapi_tags=["Admin"])


@app.get(
    "/cron/run",
    dependencies=[Depends(get_admin_user)],
    responses={status.HTTP_403_FORBIDDEN: {"description": "Not an admin user"}},
)
async def run_cronjobs():
    run_cron_jobs = sync_to_async(cron_service.run_cron_jobs)
    await run_cron_jobs()
    return Response(None, status_code=status.HTTP_200_OK)
