import logging.config
import os
import yaml
from redis import Redis
from rq import Connection, Worker
from dripdrop.settings import settings


def run_worker():
    with Connection(connection=Redis.from_url(settings.redis_url)):
        worker = Worker(["default"])
        worker.work(with_scheduler=True)


if __name__ == "__main__":
    with open(os.path.join(os.path.dirname(__file__), "./config/logging.yml")) as file:
        loaded_config = yaml.safe_load(file)
        logging.config.dictConfig(loaded_config)
    run_worker()
