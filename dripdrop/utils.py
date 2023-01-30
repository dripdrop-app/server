import asyncio
import traceback
from functools import wraps
from inspect import iscoroutinefunction, signature

from .database import database
from .logging import logger


def exception_handler(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            if iscoroutinefunction(function):
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(function(*args, **kwargs))
            return function(*args, **kwargs)
        except Exception:
            logger.error(traceback.format_exc())

    return wrapper


def worker_task(function):
    @exception_handler
    @wraps(function)
    async def wrapper(*args, **kwargs):
        parameters = signature(function).parameters
        async with database.async_create_session() as session:
            if "session" in parameters:
                kwargs["session"] = session
            return await function(*args, **kwargs)

    return wrapper
