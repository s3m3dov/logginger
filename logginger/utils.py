from logging import Logger, Handler
from typing import List


def add_handlers(logger: Logger, logging_handlers: List[Handler]) -> Logger:
    for handler in logging_handlers:
        logger.addHandler(handler)
    return logger
