import traceback
import datetime
from inspect import iscoroutinefunction
from starlette.requests import Request
from starlette.responses import Response


def endpointHandler():
    def decorator(function):
        async def wrapper(request: Request):
            try:
                if iscoroutinefunction(function):
                    return await function(request)
                else:
                    return function(request)
            except:
                print(traceback.format_exc())
                return Response(None, 400)
        return wrapper
    return decorator


def convertDBJob(job):
    return {
        key: value.__str__() if isinstance(value, datetime.datetime) else value
        for key, value in job.items()
    }
