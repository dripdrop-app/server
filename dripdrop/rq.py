from redis import Redis
from rq import Queue

from dripdrop.settings import settings

queue = Queue(connection=Redis.from_url(settings.redis_url), default_timeout=-1)
