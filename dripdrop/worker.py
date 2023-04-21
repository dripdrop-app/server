from redis import Redis
from rq import Connection, Worker
from rq.job import Job
from rq.timeouts import JobTimeoutException

import dripdrop.apps.music.tasks  # noqa
import dripdrop.apps.youtube.tasks  # noqa
from dripdrop.logger import logger
from dripdrop.settings import settings


def timeout_handler(job: Job, exc_type, exc_value, traceback):
    if isinstance(exc_value, JobTimeoutException):
        logger.exception(
            f"Job Timeout: {job.get_call_string()} ({job.args}, {job.kwargs})"
        )
        return True
    return False


if __name__ == "__main__":
    with Connection(connection=Redis.from_url(settings.redis_url)):
        worker = Worker(["high", "default"])
        worker.work(with_scheduler=True)
