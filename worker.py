import argparse
import logging.config
import os
import time
import yaml
from multiprocessing import Process
from redis import Redis
from rq import Connection, Worker

from dripdrop.settings import settings


def run_worker():
    with Connection(connection=Redis.from_url(settings.redis_url)):
        worker = Worker(["default"])
        worker.work(with_scheduler=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--logging", action="store_true")
    parser.add_argument("-w", "--workers", default=1, type=int)
    args = parser.parse_args()
    if args.logging:
        with open(
            os.path.join(os.path.dirname(__file__), "./config/logging.yml")
        ) as file:
            loaded_config = yaml.safe_load(file)
            logging.config.dictConfig(loaded_config)
    processes = list(map(lambda _: Process(target=run_worker), range(args.workers)))
    for process in processes:
        process.start()
    while True:
        time.sleep(1)
