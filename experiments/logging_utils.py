"""Minimal logging helpers for experiments CLIs (no Mentor imports)."""

from __future__ import annotations

import logging
from enum import StrEnum


class LoggingLevel(StrEnum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    SILENT = "silent"


LOGGING_LEVEL_MAP = {
    LoggingLevel.DEBUG: logging.DEBUG,
    LoggingLevel.INFO: logging.INFO,
    LoggingLevel.WARNING: logging.WARNING,
    LoggingLevel.SILENT: logging.CRITICAL + 1,
}


def setup_tool_logger(logger: logging.Logger, logging_level: int = logging.INFO):
    if logger.handlers:
        return logger
    logger.setLevel(logging_level)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging_level)
    stream_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(stream_handler)
    logger.propagate = False
    return logger
