import logging.config
import os
import yaml
from redis import Redis
from rq import Connection, Worker
from rq.job import Job
from rq.timeouts import JobTimeoutException

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
    with open(os.path.join(os.path.dirname(__file__), "../config/logging.yml")) as file:
        loaded_config = yaml.safe_load(file)
        logging.config.dictConfig(loaded_config)

    with Connection(connection=Redis.from_url(settings.redis_url)):
        worker = Worker(["default"])
        worker.work(with_scheduler=True)
