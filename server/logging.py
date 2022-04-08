import logging
from typing import List


class LevelFilter:
    def __init__(self, levels: List[str] = []) -> None:
        self.levels = set([logging.getLevelName(level) for level in levels])

    def filter(self, record: logging.LogRecord) -> bool:
        if record.levelno in self.levels:
            return super().filter(record)
        return False
