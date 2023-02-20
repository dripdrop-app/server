import traceback
from functools import wraps
from inspect import signature

from .database import database
from .logging import logger


def exception_handler(function):
    @wraps(function)
    async def wrapper(*args, **kwargs):
        try:
            return await function(*args, **kwargs)
        except Exception:
            logger.error(traceback.format_exc())

    return wrapper


def worker_task(function):
    @wraps(function)
    @exception_handler
    async def wrapper(*args, **kwargs):
        parameters = signature(function).parameters
        async with database.create_session() as session:
            if "session" in parameters:
                kwargs["session"] = session
            return await function(*args, **kwargs)

    return wrapper
