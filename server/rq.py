from redis import Redis
from rq import Queue
from server.config import config

queue = Queue(connection=Redis.from_url(config.redis_url), default_timeout=-1)
