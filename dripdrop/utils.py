import traceback
from asgiref.sync import sync_to_async
from datetime import datetime, timezone
from dripdrop.models.database import database
from dripdrop.logging import logger
from functools import wraps
from inspect import iscoroutinefunction, signature


def worker_task(function):
    @wraps(function)
    async def wrapper(*args, **kwargs):
        parameters = signature(function).parameters
        async with database.async_create_session() as session:
            if "db" in parameters:
                kwargs["db"] = session
            try:
                if not iscoroutinefunction(function):
                    func = sync_to_async(function)
                else:
                    func = function
                return await func(*args, **kwargs)
            except Exception:
                logger.error(traceback.format_exc())

    return wrapper


def get_current_time():
    return datetime.now(timezone.utc)
