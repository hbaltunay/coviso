from collections import defaultdict
from copy import deepcopy
from typing import Any

import cv2
import numpy as np
from numpy.typing import NDArray

from coviso.utils.ops import xyxy2xywh


class ZoneTracker:
    def __init__(self, cfg: dict[str, Any]) -> None:
        self.cfg = cfg
        self.areas = self.set_areas(cfg)
        self.areas_org = deepcopy(self.areas)
        self.frame_num = 0
        self.filled_areas = []

    def create_mask(self, size: tuple[int, int]) -> None:
        """
        Args:
            size (tuple): The dimensions of the processed video frame.
        """
        self.size = size
        self.mask = np.zeros(size)
        for i, name in enumerate(self.cfg["areas"]):
            area = self.areas[name]["area"]
            cv2.fillPoly(self.mask, [np.array(area)], color=i + 1)

    def set_areas(self, cfg: dict[str, Any]) -> dict[str, Any]:
        """
        Args:
            cfg (dict): Dictionary of process configuration parameters.
        Returns:
            dict: Dictionary containing area information.
        """
        areas = defaultdict(dict)
        for name, area in cfg["areas"].items():
            areas[name]["area"] = area
            areas[name]["statu"] = 0
        return areas

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
                frame, (int(x), int(y)), radius=5, color=(255, 255, 255), thickness=-1
            )
        return frame

    def draw_areas(self, frame: NDArray[Any], areas: dict[str, Any]) -> NDArray[Any]:
        """
        Args:
            frame (NDArray): The image of the video frame.
            areas (dict): Dictionary containing area information.
        Returns:
            NDArray: The image of the processed video frame.
        """
        for area in areas.values():
            cv2.polylines(
                img=frame,
                pts=[np.array([area["area"]])],
                isClosed=True,
                color=(0, 0, 255) if area["statu"] else (0, 255, 0),
                thickness=2,
            )

            for x, y in area["area"]:
                cv2.circle(
                    img=frame,
                    center=(x, y),
                    radius=5,
                    color=(255, 0, 0),
                    thickness=-1,
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
        frame = self.draw_areas(frame, self.areas)
        return frame

    def compute(self, result: dict[str, Any]):
        """
        Args:
            result (Any): The output results from the model.
        """
        for res in result:
            x, y, _, h = xyxy2xywh(res[:4].numpy())
            statu = int(self.mask[min(int(y + (h / 2)) - 1, self.size[0]), int(x)])

            if not (statu in self.filled_areas) and statu > 0:
                self.areas[f"area_{str(statu)}"]["statu"] = 1
                self.filled_areas.append(statu)
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
            self.filled_areas = []
            self.areas = deepcopy(self.areas_org)

        return frame, self.areas
