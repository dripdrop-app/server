import logging.config
import os
import yaml

with open(os.path.join(os.path.dirname(__file__), "./logging.yml")) as file:
    loaded_config = yaml.safe_load(file)
    logging.config.dictConfig(loaded_config)
