import logging
import os
from pathlib import Path
from typing import Any

LOGGER_NAME = "COVISO"
LOGGER_HANDLERS = ["stream", "file"]


class CLogger:
    def __init__(
        self,
        name: str | None = None,
        handlers: list[str] | None = None,
        filename: str | Path = "coviso.log",
        overwrite: bool = False,
    ) -> None:
        """
        Args:
            name (str): The name of the logger.
            handlers (List[str] | None): List of handler names to be used.
            filename: (str | Path): The name of the file where logs will be written.
            overwrite (bool): If True, the existing log file will be overwritten.
                Otherwise, a new log file will be created.
        """
        self.name = name or LOGGER_NAME
        self.handlers = handlers
        self.filename = filename
        self.overwrite = overwrite

        self.logger = logging.getLogger(name=self.name)

        if self.logger.handlers:
            self.logger.handlers.clear()

        self._configure_logger()

        if not self.logger.handlers:
            raise ValueError(
                f"Logger must have at least one handler configured. Visible Handlers: {LOGGER_HANDLERS}"
            )

    def _configure_logger(self) -> None:

        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        if self.handlers is None:
            self.handlers = ["stream"]

        if "file" in self.handlers:
            file_path = Path(self.filename)

            if file_path.exists() and not self.overwrite:
                os.remove(self.filename)

            file_path.parent.mkdir(parents=True, exist_ok=True)
            handler = logging.FileHandler(self.filename, mode="a", encoding="utf-8")
            formatter = logging.Formatter(
                "%(asctime)s:%(name)s:%(levelname)s:%(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        if "stream" in self.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(name)s:%(levelname)s:%(message)s",
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def debug(self, msg: str, *args: Any, **kwargs: Any):
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any):
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args: Any, **kwargs: Any):
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any):
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args: Any, **kwargs: Any):
        self.logger.critical(msg, *args, **kwargs)


if __name__ == "__main__":
    logger = CLogger()
