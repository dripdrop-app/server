import logging
import os
from logging.handlers import RotatingFileHandler


logger = logging.getLogger("logger")
handler = RotatingFileHandler(
    os.path.join(os.path.dirname(__file__), "../logs/logging.log"),
    maxBytes=10000,
    backupCount=10,
)
logger.addHandler(handler)
