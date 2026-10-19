import logging
from collections import defaultdict
from pathlib import Path

import cv2
import numpy as np

from coviso.detect.core import Detection
from coviso.solution.base import BaseSolution, CoordinateData
from coviso.solution.state import ZoneState
from coviso.tool.config import Config

LOGGER = logging.getLogger("coviso")


class ZoneTracker(BaseSolution):
    def __init__(self, config_path: Path, strategy: str = "plain") -> None:
        super().__init__(config_path)
        self.strategy = strategy
        self.state: ZoneState = ZoneState()
        self.zones: CoordinateData = {}
        self.mask: np.ndarray = np.empty(0)

        if self.strategy == "tracked":
            self.active_strategy = self.tracked_strategy
        else:
            self.active_strategy = self.plain_strategy

    def init(self) -> bool:
        config = Config(self.config_path)
        if not config.load():
            return False

        self.name = config.get_or("name", "")
        if not self.name:
            return False

        imgsz_dict: tuple[int, int] = config.get_or(
            "imgsz", {"weight": 0, "height": 0}
        )
        if imgsz_dict["width"] <= 0 or imgsz_dict["height"] <= 0:
            return False
        self.imgsz = imgsz_dict["width"], imgsz_dict["height"]

        self.zones = config.get_or("points", {})
        if not self.zones:
            return False

        return self.create_mask()

    def create_mask(self) -> bool:
        self.mask = np.zeros((self.imgsz[1], self.imgsz[0]), dtype=np.uint8)

        zone_id = 1
        max_zone_id = 255

        for _, zone_map in self.zones.items():
            if "zone" not in zone_map:
                continue

            zone_points_raw = zone_map["zone"]
            zone_points = []

            for pt in zone_points_raw:
                if (
                    len(pt) == 2
                    and pt[0] >= 0
                    and pt[0] < self.imgsz[0]
                    and pt[1] >= 0
                    and pt[1] < self.imgsz[1]
                ):
                    zone_points.append(pt)

            if len(zone_points) < 3:
                continue

            current_zone = [np.array(zone_points, dtype=np.int32)]
            cv2.fillPoly(self.mask, current_zone, zone_id)

            self.state.add(zone_id, zone_points)

            zone_id += 1

            if zone_id > max_zone_id:
                LOGGER.warn("Zone limit reached!")
                return True

        self.state.add(0, [])
        self.zone_num = zone_id - 1

        return True

    def plain_strategy(self, detections: list[Detection]) -> None:
        zone_freq = defaultdict(int)
        s1, s2 = self.mask.shape

        for det in detections:
            x = int(det.bbox.x)
            y = int(det.bbox.y)

            if x < 0 or x >= s2 or y < 0 or y >= s1:
                continue

            value = int(self.mask[y][x])

            zone_freq[value] += 1

        self.state.update_plain(zone_freq)

    def tracked_strategy(self, detections: list[Detection]) -> None:
        s1, s2 = self.mask.shape

        for det in detections:
            x = int(det.bbox.x)
            y = int(det.bbox.y)
            track_id = det.id

            if x < 0 or x >= s2 or y < 0 or y >= s1:
                continue

            value = int(self.mask[y][x])

            self.zone_infos[value].in_zone.append(track_id)

        self.state.update_tracked()

    def process(self, image: np.ndarray, detections: list[Detection]) -> None:
        self.active_strategy(detections)
        self.draw(image, detections)

    def draw(self, image: np.ndarray, detections: list[Detection]) -> None:
        for id, zone_info in self.state.zone_infos.items():
            if id == 0:
                continue
            cv2.fillPoly(
                image, [np.array(zone_info.zone, dtype=np.int32)], (id)
            )

    def get_state_info_str(self) -> list[str]:
        return self.state.summary()
