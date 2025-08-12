from collections import defaultdict
from copy import deepcopy
from typing import Any

import cv2
import numpy as np
from numpy.typing import NDArray

from coviso.utils.ops import xyxy2xywh

from .base import Tracker


class ZoneTracker(Tracker):
    def __init__(self, cfg: dict[str, Any]) -> None:
        """
        Args:
            cfg (dict): Dictionary of process configuration parameters.
        """
        self.setup(cfg)

    def create_mask(self, size: tuple[int, int]) -> None:
        """
        Args:
            size (tuple): The dimensions of the processed video frame.
        """
        self.size = size
        self.mask = np.zeros(size)
        for i, name in enumerate(self.cfg["polys"]):
            poly = self.polys[name]["poly"]
            cv2.fillPoly(img=self.mask, pts=[np.array(poly)], color=i + 1)

    def setup(self, cfg: dict[str, Any]) -> None:
        """
        Args:
            cfg (dict): Dictionary of process configuration parameters.
        """
        self.cfg = cfg
        self.polys = self.set_polys(cfg)
        self.polys_org = deepcopy(self.polys)
        self.frame_num = 0
        self.filled_polys = []

    def set_polys(self, cfg: dict[str, Any]) -> dict[str, Any]:
        """
        Args:
            cfg (dict): Dictionary of process configuration parameters.
        Returns:
            dict: Dictionary containing poly information.
        """
        polys = defaultdict(dict)
        for name, poly in cfg["polys"].items():
            polys[name]["poly"] = poly
            polys[name]["statu"] = 0
        return polys

    def draw_result(self, frame: NDArray[Any], result: Any) -> NDArray[Any]:
        """
        Args:
            frame (NDArray): The image of the video frame.
            result (Any): The output results from the model.
        Returns:
            NDArray: The image of the processed video frame.
        """
        xyxy = result[:, :4].numpy().astype(int)
        for x1, y1, x2, y2 in xyxy:
            cv2.rectangle(frame, (x1, y1), (x2, y2), color=(0, 0, 0), thickness=1)
            x, y, _, h = xyxy2xywh(np.array([x1, y1, x2, y2]))
            x, y = x, min(int(y + (h / 2)), self.size[0]) - 1
            cv2.circle(
                img=frame,
                center=(int(x), int(y)),
                radius=5,
                color=(255, 255, 255),
                thickness=-1,
            )
        return frame

    def draw_polys(self, frame: NDArray[Any], polys: dict[str, Any]) -> NDArray[Any]:
        """
        Args:
            frame (NDArray): The image of the video frame.
            polys (dict): Dictionary containing poly information.
        Returns:
            NDArray: The image of the processed video frame.
        """
        for poly in polys.values():
            cv2.polylines(
                img=frame,
                pts=[np.array([poly["poly"]])],
                isClosed=True,
                color=(0, 0, 255) if poly["statu"] else (0, 255, 0),
                thickness=2,
            )
        return frame

    def draw(self, frame: Any, result: Any) -> NDArray[Any]:
        """
        Args:
            frame (NDArray): The image of the video frame.
            result (Any): The output results from the model.
        Returns:
            NDArray: The image of the processed video frame.
        """
        frame = self.draw_result(frame, result)
        frame = self.draw_polys(frame, self.polys)
        return frame

    def compute(self, result: Any):
        """
        Args:
            result (Any): The output results from the model.
        """
        for res in result:
            x, y, _, h = xyxy2xywh(res[:4].numpy())
            statu = int(self.mask[min(int(y + (h / 2)) - 1, self.size[0]), int(x)])

            if not (statu in self.filled_polys) and statu > 0:
                self.polys[f"poly_{str(statu)}"]["statu"] = 1
                self.filled_polys.append(statu)
        self.frame_num += 1

    def process(
        self, frame: NDArray[Any], result: Any
    ) -> tuple[NDArray[Any], dict[str, Any]]:
        """
        Args:
            frame (NDArray): The image of the video frame.
            result (Any): The output results from the model.
        Returns:
            tuple: A tuple containing the processed video frame image and the field information dictionary.
        """
        self.compute(result)
        self.draw(frame, result)

        if self.frame_num == 20:
            self.frame_num = 0
            self.filled_polys = []
            self.polys = deepcopy(self.polys_org)

        return frame, self.polys
