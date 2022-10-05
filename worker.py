import logging.config
import os
import yaml
from redis import Redis
from rq import Connection, Worker
from server.config import config

with open(os.path.join(os.path.dirname(__file__), "./config/logging.yml")) as file:
    loaded_config = yaml.safe_load(file)
    logging.config.dictConfig(loaded_config)

with Connection(connection=Redis.from_url(config.redis_url)):
    worker = Worker(["default"])
    worker.work(with_scheduler=True)
