import argparse
import logging.config
import os
import yaml
from redis import Redis
from rq import Connection, Worker

from dripdrop.settings import settings


if __name__ == "__main__":
    with Connection(connection=Redis.from_url(settings.redis_url)):
        worker = Worker(["default"])
        worker.work(with_scheduler=True)
