import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("coviso")


class Config:
    def __init__(self, config_path: Path) -> None:
        self._config_path: Path = Path(config_path)
        self._config_json: dict[str, Any] = {}

    def load(self) -> bool:
        if not self._config_path.exists():
            logger.error(f"Config file not found: {self._config_path}")
            return False

        try:
            with open(self._config_path, encoding="utf-8") as file:
                self._config_json = json.load(file)
        except json.JSONDecodeError as e:
            logger.error(
                f"JSON parse error in config file {self._config_path}: {e}"
            )
            return False
        except Exception as e:
            logger.error(f"Unexpected error while reading config file: {e}")
            return False

        logger.info(f"Config file loaded successfully: {self._config_path}")
        return True

    def get(self, key: str) -> Any:
        return self._config_json[key]

    def get_or[T](self, key: str, default_value: T) -> T:
        return self._config_json.get(key, default_value)
