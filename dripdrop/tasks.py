import traceback
from functools import wraps
from inspect import signature

from dripdrop.services import database

from .logging import logger


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
            format_arguments = ", ".join(args) + ", ".join(
                [f"{kwarg}={kwargs[kwarg]}" for kwarg in kwargs]
            )
            logger.info(
                f"{function.__module__}.{function.__name__}({format_arguments})"
            )
            if "session" in parameters and "session" not in kwargs:
                async with database.create_session() as session:
                    kwargs["session"] = session
                    return await function(*args, **kwargs)
            else:
                return await function(*args, **kwargs)

        return wrapper

    return decorator
