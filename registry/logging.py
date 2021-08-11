"""
Logging configuration.
"""

import logging
import logging.handlers
import pathlib

__all__ = ["init"]


def init(
    filename: pathlib.Path,
    *,
    level: int = logging.DEBUG,
    fmt: str = "[%(asctime)s] %(levelname)s %(module)s:%(lineno)d %(message)s",
    datefmt: str = "%Y-%m-%d %H:%M:%S",
    maxBytes: int = 10 * 1024 * 1024,
    backupCount: int = 4,  # plus the current log file -> 50 MiB total
) -> None:
    """
    Adds a stream handler and a rotating file handler to the root logger.
    """

    filename.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger()
    formatter = logging.Formatter(fmt, datefmt=datefmt)

    for handler in [
        logging.StreamHandler(),
        logging.handlers.RotatingFileHandler(
            filename, maxBytes=maxBytes, backupCount=backupCount
        ),
    ]:
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(level)
