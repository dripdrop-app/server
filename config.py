import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "generic": {
            "format": "%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
            "datefmt": "[%Y-%m-%d %H:%M:%S %z]",
            "class": "logging.Formatter",
        }
    },
    "filters": {
        "info": {
            "()": "server.logging.ErrorFilter",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": "ext://sys.stdout",
            "filters": ["info"],
        },
        "error_console": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "": {"level": "INFO", "handlers": ["console", "error_console"]},
        "gunicorn.error": {"level": "INFO", "handlers": ["error_console", "console"]},
        "gunicorn.access": {"level": "INFO", "handlers": ["console"]},
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
