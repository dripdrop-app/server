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
        "error": {
            "()": "server.logging.LevelFilter",
            "levels": ["WARNING", "CRITICAL", "ERROR"],
        },
        "info": {"()": "server.logging.LevelFilter", "levels": ["INFO", "DEBUG"]},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": "ext://sys.stdout",
            "filters": ["info"],
        },
        "error_console": {
            "class": "logging.StreamHandler",
            "formatter": "generic",
            "stream": "ext://sys.stderr",
            "filters": ["error"],
        },
    },
    "loggers": {
        "root": {"level": "INFO", "handlers": ["console", "error_console"]},
        "gunicorn.error": {"level": "INFO", "handlers": ["error_console", "console"]},
        "gunicorn.access": {"level": "INFO", "handlers": ["console"]},
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
