import logging
from logging.handlers import RotatingFileHandler

from mcp_pdf_finder.config import settings


LOG_FILE = settings.logging_directory / "app.log"

LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)-8s | "
    "%(name)s | "
    "%(message)s"
)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging() -> None:
    LOG_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    root_logger = logging.getLogger()

    if root_logger.handlers:
        return

    log_level = getattr(
        logging,
        settings.logging_level,
        logging.INFO,
    )

    root_logger.setLevel(log_level)

    formatter = logging.Formatter(
        fmt=LOG_FORMAT,
        datefmt=DATE_FORMAT,
    )

    handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=10_000_000,
        backupCount=5,
        encoding="utf-8",
    )

    handler.setLevel(log_level)
    handler.setFormatter(formatter)

    root_logger.addHandler(handler)