import traceback
from asgiref.sync import async_to_sync
from functools import wraps
from inspect import iscoroutinefunction, signature

from .database import database
from .logging import logger


def exception_handler(function):
    @wraps(function)
    def sync_wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception:
            logger.error(traceback.format_exc())

    @wraps(function)
    async def async_wrapper(*args, **kwargs):
        try:
            return await function(*args, **kwargs)
        except Exception:
            logger.error(traceback.format_exc())

    return async_wrapper if iscoroutinefunction(function) else sync_wrapper


def worker_task(function):
    @exception_handler
    @wraps(function)
    def sync_wrapper(*args, **kwargs):
        parameters = signature(function).parameters
        with database.create_session() as session:
            if "session" in parameters:
                kwargs["session"] = session
            return function(*args, **kwargs)

    @exception_handler
    @wraps(function)
    def async_wrapper(*args, **kwargs):
        async def _internal_wrapper(*args, **kwargs):
            parameters = signature(function).parameters
            async with database.async_create_session() as session:
                if "session" in parameters:
                    kwargs["session"] = session
                return await function(*args, **kwargs)

        func = async_to_sync(_internal_wrapper)
        return func(*args, **kwargs)

    return async_wrapper if iscoroutinefunction(function) else sync_wrapper
