import traceback
from asgiref.sync import sync_to_async
from functools import wraps
from inspect import iscoroutinefunction
from server.logging import logger
from server.models.main import create_db


def exception_handler(function):
    @wraps(function)
    async def wrapper(*args, **kwargs):
        nonlocal function
        try:
            if not iscoroutinefunction(function):
                function = sync_to_async(function)
            return await function(*args, **kwargs)
        except Exception:
            logger.error(traceback.format_exc())
            return None

    return wrapper


def worker_task(function):
    @wraps(function)
    async def wrapper(*args, **kwargs):
        if iscoroutinefunction(function):
            db = create_db()
            await db.connect()
            result = await function(*args, **kwargs, db=db)
            await db.disconnect()
            return result
        func = sync_to_async(function)
        return await func(*args, **kwargs)

    return wrapper
