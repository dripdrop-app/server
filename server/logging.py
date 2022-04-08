import logging
import sys
import uvicorn.config
import uvicorn.logging
from typing import List


class CustomFilter(logging.Filter):
    def __init__(self, name: str = ..., levels: List[int] = []) -> None:
        super().__init__(name)
        self.levels = set(levels)

    def filter(self, record: logging.LogRecord) -> bool:
        if record.levelno in self.levels:
            return super().filter(record)
        return False


def init_logging():
    def remove_handlers(logger: logging.Logger):
        handlers = logger.handlers
        for handler in handlers:
            logger.removeHandler(handler)

    default_formatter = uvicorn.logging.DefaultFormatter(
        uvicorn.config.LOGGING_CONFIG["formatters"]["default"]["fmt"]
    )
    access_formatter = uvicorn.logging.AccessFormatter(
        uvicorn.config.LOGGING_CONFIG["formatters"]["access"]["fmt"]
    )

    uvicorn_access_logger = logging.getLogger("uvicorn.access")
    uvicorn_err_logger = logging.getLogger("uvicorn.error")

    uvicorn_access_logger.propagate = False
    uvicorn_err_logger.propagate = False

    uvicorn_access_logger.setLevel(logging.INFO)
    uvicorn_err_logger.setLevel(logging.INFO)

    remove_handlers(uvicorn_access_logger)
    remove_handlers(uvicorn_err_logger)

    log_stream = logging.StreamHandler(sys.stdout)
    log_stream.setFormatter(access_formatter)
    uvicorn_access_logger.addHandler(log_stream)
    uvicorn_access_logger.addFilter(
        CustomFilter("uvicorn.access", [logging.INFO, logging.WARNING])
    )

    error_stream = logging.StreamHandler(sys.stderr)
    error_stream.setFormatter(default_formatter)
    error_stream.addFilter(
        CustomFilter(
            "uvicorn.error", [logging.CRITICAL, logging.ERROR, logging.WARNING]
        )
    )
    uvicorn_err_logger.addHandler(error_stream)

    log_stream = logging.StreamHandler(sys.stdout)
    log_stream.setFormatter(default_formatter)
    log_stream.addFilter(CustomFilter("uvicorn.error", [logging.INFO]))
    uvicorn_err_logger.addHandler(log_stream)

    return uvicorn_err_logger


logger = init_logging()
