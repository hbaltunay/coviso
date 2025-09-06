import json
from typing import Any

import yaml

from ..loggers import CLogger

logger = CLogger(__name__)


def check_unique_name(name: str, name_list: list[str]) -> str:
    if name not in name_list:
        return name

    for i in range(2, 999):
        new_name = f"{name}_{i}"
        if new_name not in name_list:
            return new_name

    logger.info(
        "The file name limit has been exceeded. From now on, new files will be saved with the same name. 📂⚠️"
    )

    return f"{name}_999"


class YAMLFile:
    def __init__(self) -> None:
        self.cfg_dict = None

    def read(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            self.cfg_dict = yaml.safe_load(f)
        return self.cfg_dict

    def write(self, file_path: str, cfg_dict: dict[str, Any]) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            yaml.dump(cfg_dict, f, default_flow_style=False)


class JSONFile:
    def __init__(self):
        self.cfg_dict = None

    def read(self, file_path: str) -> dict[str, Any]:
        try:
            with open(file_path, "r") as f:
                self.cfg_dict = json.load(f)
        except json.JSONDecodeError:
            logger.info("Json file is empty.")
            return {}

        return self.cfg_dict

    def write(self, file_path: str, cfg_dict: dict[str, Any]) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(cfg_dict, f, ensure_ascii=False, indent=2)


class CFGManager:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._files = {
            "json": JSONFile(),
            "yaml": YAMLFile(),
        }

    @property
    def cfg_dict(self) -> dict[str, Any]:
        cfg_dict = self.read_file()
        return cfg_dict

    @staticmethod
    def get_type(file_path: str) -> str:
        return file_path.split(".")[-1]

    def read_file(self) -> dict[str, Any]:
        file_type = self.get_type(self.file_path)
        reader = self._files.get(file_type)
        if reader:
            cfg_dict = reader.read(self.file_path)
            return cfg_dict
        else:
            raise ValueError("Unsupported file type.")

    def write_file(self, cfg: dict[str, Any]) -> None:
        cfg_dict = self.cfg_dict
        cfg_dict.update(cfg)
        file_type = self.get_type(self.file_path)
        writer = self._files.get(file_type)
        if writer:
            writer.write(self.file_path, cfg_dict)
        else:
            raise ValueError("Unsupported file type.")
