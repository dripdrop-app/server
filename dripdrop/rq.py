from rq import Queue

from dripdrop.redis import redis
from dripdrop.settings import ENV, settings

queue = Queue(
    connection=redis,
    default_timeout=-1,
    is_async=settings.env != ENV.TESTING,
)
