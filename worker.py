import argparse
import logging.config
import os
import yaml
from redis import Redis
from rq import Connection, Worker

from dripdrop.settings import settings


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--logging", action="store_true")
    args = parser.parse_args()

    if args.logging:
        with open(
            os.path.join(os.path.dirname(__file__), "./config/logging.yml")
        ) as file:
            loaded_config = yaml.safe_load(file)
            logging.config.dictConfig(loaded_config)

    with Connection(connection=Redis.from_url(settings.redis_url)):
        worker = Worker(["default"])
        worker.work(with_scheduler=True)
