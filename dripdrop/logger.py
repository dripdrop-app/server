import logging.config
import os

import yaml

with open(os.path.join(os.path.dirname(__file__), "../config/logging.yml")) as file:
    loaded_config = yaml.safe_load(file)
    logging.config.dictConfig(loaded_config)

logger = logging.getLogger("dripdrop")
