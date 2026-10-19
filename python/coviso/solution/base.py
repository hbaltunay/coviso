from abc import ABC, abstractmethod
from pathlib import Path

import numpy as np

from coviso.detect.core import Detection

type Coordinate2D = list[int]
type CoordinateList = list[Coordinate2D]
type InnerMap = dict[str, CoordinateList]
type CoordinateData = dict[str, InnerMap]


class BaseSolution(ABC):
    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path
        self.name: str = ""
        self.imgsz: list[int] = [0, 0]

    @abstractmethod
    def process(self, image: np.ndarray, detections: list[Detection]) -> None:
        pass
