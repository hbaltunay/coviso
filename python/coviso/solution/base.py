from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np

from coviso.detect.core import Detection
from coviso.tool.config import Config

type Coordinate2D = list[int]
type CoordinateList = list[Coordinate2D]
type InnerMap = dict[str, CoordinateList]
type CoordinateData = dict[str, InnerMap]


class BaseSolution(ABC):
    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path
        self.name: str = ""
        self.imgsz: list[int] = [0, 0]

        self.config: Config = Config(self.config_path)
        if not self.config.load():
            raise NotImplementedError

        imgsz_dict: tuple[int, int] = self.config.get_or(
            "imgsz", {"weight": 0, "height": 0}
        )
        if imgsz_dict["width"] <= 0 or imgsz_dict["height"] <= 0:
            raise NotImplementedError
        self.imgsz = imgsz_dict["width"], imgsz_dict["height"]

    @abstractmethod
    def process(self, image: np.ndarray, detections: list[Detection]) -> None:
        pass
