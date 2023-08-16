import logging


class Filter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return (
            record.levelno < logging.WARNING
            or record.getMessage().find("/healtcheck") != -1
        )
