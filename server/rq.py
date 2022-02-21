from redis import Redis
from rq import Queue

queue = Queue(connection=Redis(), default_timeout=-1)
