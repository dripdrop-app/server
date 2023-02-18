import logging.config
import os
import yaml
from redis import Redis
from rq import Connection, Worker

from dripdrop.settings import settings, ENV


if __name__ == "__main__":
    if settings.env == ENV.PRODUCTION:
        with open(os.path.join(os.path.dirname(__file__), "./logging.yml")) as file:
            loaded_config = yaml.safe_load(file)
            logging.config.dictConfig(loaded_config)

    with Connection(connection=Redis.from_url(settings.redis_url)):
        worker = Worker(["default"])
        worker.work(with_scheduler=True)
