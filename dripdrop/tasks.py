import traceback
from functools import wraps
from inspect import signature
from rq import get_current_job

from dripdrop.services import database

from .logger import logger


def exception_handler(raise_exception=True):
    def decorator(function):
        @wraps(function)
        async def wrapper(*args, **kwargs):
            try:
                return await function(*args, **kwargs)
            except Exception as e:
                logger.error(traceback.format_exc())
                if raise_exception:
                    raise e

        return wrapper

    return decorator


def worker_task(raise_exception=True):
    def decorator(function):
        @wraps(function)
        @exception_handler(raise_exception=raise_exception)
        async def wrapper(*args, **kwargs):
            func_signature = signature(function)
            parameters = func_signature.parameters
            if "session" in parameters and "session" not in kwargs:
                async with database.create_session() as session:
                    kwargs["session"] = session
                    if "job" in parameters:
                        kwargs["job"] = get_current_job()
                    return await function(*args, **kwargs)
            else:
                return await function(*args, **kwargs)

        return wrapper

    return decorator
