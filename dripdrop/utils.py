import traceback
from asgiref.sync import sync_to_async
from functools import wraps
from inspect import iscoroutinefunction, signature
from dripdrop.database import create_session
from dripdrop.logging import logger


def worker_task(function):
    @wraps(function)
    async def wrapper(*args, **kwargs):
        parameters = signature(function).parameters
        async with create_session() as db:
            if "db" in parameters:
                kwargs["db"] = db
            try:
                if not iscoroutinefunction(function):
                    func = sync_to_async(function)
                else:
                    func = function
                return await func(*args, **kwargs)
            except Exception:
                logger.error(traceback.format_exc())

    return wrapper
