import logging
import logging.config
import os
from copy import copy
from pathlib import Path

from .utils import ANSI, LEVEL_COLORS

LOGGER_HANDLERS = ["stream", "file"]
LOGGER_FILENAME = os.getenv("LOGGER_FILENAME", "run.log")
# CVS: Coviso Virtual Storage
LOGGER_FILEPATH = os.getenv("LOGGER_FILEPATH", "./cvs")

FILE_OVERWRITE = os.getenv("FILE_OVERWRITE", "false") == "true"
ON_FILE_HANDLER = os.getenv("ON_FİLE_HANDLER", "false").lower() == "true"


LOGGER_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "stream_fmt": {
            "()": "coviso.tool.logger.StreamFormatter",
            "fmt": "%(name)s %(levelname)s %(message)s",
        },
        "file_fmt": {
            "()": "logging.Formatter",
            "fmt": "%(asctime)s:%(name)s:%(levelname)s:%(message)s",
        },
    },
    "handlers": {
        "stream": {
            "formatter": "stream_fmt",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "formatter": "file_fmt",
            "class": "logging.FileHandler",
            "filename": "run.log",
            "mode": "a",
            "encoding": "utf-8",
            "delay": True,
        },
    },
    "loggers": {
        "coviso": {"handlers": ["stream"], "level": "INFO", "propagate": False},
    },
}


class StreamFormatter(logging.Formatter):
    def formatMessage(self, record: logging.LogRecord):  # noqa
        recopy = copy(record)
        color = LEVEL_COLORS.get(recopy.levelno, ANSI.BLUE)
        recopy.name = (
            ANSI.CYAN + f"{recopy.name.upper().center(12):.12}" + ANSI.RESET
        )
        recopy.levelname = (
            f"{color}["
            + f"{recopy.levelname.center(10):.10}"
            + f"]{ANSI.RESET} :"
        )

        return super().formatMessage(recopy)


def configure_logging() -> None:
    """
    Configure Logging
    """

    if ON_FILE_HANDLER:
        file_path = Path(LOGGER_FILEPATH) / LOGGER_FILENAME

        LOGGER_CONFIG["handlers"]["file"]["filename"] = str(file_path)

        for logger_name in LOGGER_CONFIG["loggers"]:
            LOGGER_CONFIG["loggers"][logger_name]["handlers"].append("file")

        if file_path.exists() and not FILE_OVERWRITE:
            os.remove(file_path)

        file_path.parent.mkdir(parents=True, exist_ok=True)

    logging.config.dictConfig(LOGGER_CONFIG)
