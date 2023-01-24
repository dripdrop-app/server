import traceback
from asgiref.sync import sync_to_async
from datetime import datetime
from functools import wraps
from inspect import iscoroutinefunction, signature

from .database import database
from .logging import logger
from .settings import settings


def exception_handler(function):
    @wraps(function)
    async def wrapper(*args, **kwargs):
        try:
            if not iscoroutinefunction(function):
                func = sync_to_async(function)
            else:
                func = function
            return await func(*args, **kwargs)
        except Exception:
            logger.error(traceback.format_exc())

    return wrapper


def worker_task(function):
    @wraps(function)
    async def wrapper(*args, **kwargs):
        parameters = signature(function).parameters
        async with database.async_create_session() as session:
            if "session" in parameters:
                kwargs["session"] = session
                func = exception_handler(function)
            return await func(*args, **kwargs)

    return wrapper


def get_current_time():
    return datetime.now(tz=settings.timezone)
