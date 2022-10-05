import logging.config
import yaml

with open("log_config.yml") as file:
    loaded_config = yaml.safe_load(file)
    logging.config.dictConfig(loaded_config)
