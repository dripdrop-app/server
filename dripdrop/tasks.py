import asyncio
from functools import wraps
from inspect import signature, iscoroutinefunction
from rq import get_current_job

from dripdrop.services import database


async def _async_task_runner(function, *args, **kwargs):
    func_signature = signature(function)
    parameters = func_signature.parameters
    if "session" in parameters and "session" not in kwargs:
        async with database.create_session() as session:
            kwargs["session"] = session
            return await function(*args, **kwargs)


def worker_task(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        func_signature = signature(function)
        parameters = func_signature.parameters
        if "job" in parameters:
            kwargs["job"] = get_current_job()

        if iscoroutinefunction(function):
            return asyncio.run(_async_task_runner(function, *args, **kwargs))
        else:
            return function(*args, **kwargs)

    return wrapper
