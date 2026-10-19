import logging
import math
from pathlib import Path

import cv2
import numpy as np

from coviso.detect.core import Detection
from coviso.solution.base import BaseSolution, CoordinateData
from coviso.solution.state import LineState, TrackInfo
from coviso.tool.config import Config

LOGGER = logging.getLogger("coviso")


class LineTracker(BaseSolution):
    def __init__(self, config_path: Path) -> None:
        super().__init__(config_path)
        self.mask: np.ndarray = np.empty(0)
        self.lines: CoordinateData = {}
        self.line_num: int = 0
        self.state: LineState = LineState()

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

        self.lines = config.get_or("points", {})
        if not self.lines:
            return False

        return self.create_mask()

    def create_line_zones(
        self,
        first_point: list[int],
        second_point: list[int],
        width: float,
        angle: float,
    ) -> list:
        x1, y1 = first_point
        x2, y2 = second_point

        dx = float(x2 - x1)
        dy = float(y2 - y1)
        line_length = math.sqrt(dx * dx + dy * dy)

        if line_length < 0.001:
            return []

        base_angle_rad = math.atan2(dy, dx)

        offset_angle_rad = (angle * math.pi) / 180.0
        final_angle_rad = base_angle_rad + offset_angle_rad

        shift_x = width * math.cos(final_angle_rad)
        shift_y = width * math.sin(final_angle_rad)

        line_entry = np.array(
            [
                [x1, y1],
                [x2, y2],
                [int(x2 + shift_x), int(y2 + shift_y)],
                [int(x1 + shift_x), int(y1 + shift_y)],
            ],
            dtype=np.int32,
        )

        line_exit = np.array(
            [
                [x1, y1],
                [x2, y2],
                [int(x2 - shift_x), int(y2 - shift_y)],
                [int(x1 - shift_x), int(y1 - shift_y)],
            ],
            dtype=np.int32,
        )

        return [line_entry, line_exit]

    def create_mask(self) -> bool:
        self.mask = np.zeros((self.imgsz[1], self.imgsz[0]), dtype=np.uint8)

        line_id = 1
        max_line_id = 254

        for _line_name, line_map in self.lines.items():
            if "line" not in line_map:
                continue

            line_points_raw = line_map["line"]
            line_points = []

            w = 0
            a = 0
            first_point = [0.0, 0.0]
            second_point = [0.0, 0.0]

            for i in range(3):
                pt = line_points_raw[i]
                if i < 2:
                    if (
                        len(pt) == 2
                        and pt[0] >= 0
                        and pt[0] < self.imgsz[0]
                        and pt[1] >= 0
                        and pt[1] < self.imgsz[1]
                    ):
                        line_points.append(pt)

                        if i == 0:
                            first_point = pt
                        else:
                            second_point = pt
                else:
                    if (
                        len(pt) == 2
                        and pt[0] >= 0
                        and pt[0] < max(self.imgsz)
                        and pt[1] >= 45
                        and pt[1] <= 135
                    ):
                        line_points.append(pt)
                        w = pt[0]
                        a = pt[1]

            if len(line_points) != 3:
                continue

            line_zones = self.create_line_zones(first_point, second_point, w, a)
            for line_zone in line_zones:
                current_zone = [np.array(line_zone, dtype=np.int32)]
                cv2.fillPoly(self.mask, current_zone, line_id)

                self.state.add(line_id, line_zone)

                line_id += 1

            if line_id > max_line_id:
                LOGGER.warn("Line limit reached!")
                return True

        self.line_num = line_id

        return True

    def process(self, image: np.ndarray, detections: list[Detection]) -> None:
        line_infos = self.state.line_infos

        s1, s2 = self.mask.shape

        for det in detections:
            x = int(det.bbox.x)
            y = int(det.bbox.y)
            track_id = int(det.id)

            if x < 0 or x >= s2 or y < 0 or y >= s1:
                continue

            value = int(self.mask[y][x])

            if track_id not in self.state.track_infos:
                self.state.track_infos[track_id] = TrackInfo()

            t = self.state.track_infos[track_id]

            t.current_line = value

            if t.current_line != t.last_line:
                if t.passed_num == 0:
                    t.passed_num = (
                        t.last_line if (t.last_line > 0) else t.current_line
                    )
                elif not t.passed and t.current_line == 0:
                    t.passed_num = 0
                elif t.passed and t.current_line == 0:
                    passed_line = line_infos[t.last_line].line_num
                    line_infos[passed_line].count += 1
                    t.passed = False
                    t.passed_num = 0
                elif t.current_line == t.passed_num:
                    t.passed = False
                elif t.last_line == line_infos[t.current_line].line_num:
                    t.passed = True
                else:
                    LOGGER.warn("Invalid action performed.")

            t.last_line = t.current_line

        self.state.update()
        self.draw(image, detections)

    def draw(self, image: np.ndarray, detections: list[Detection]) -> None:
        for id, line_info in self.state.line_infos.items():
            if id == 0:
                continue
            cv2.fillPoly(image, [line_info.line], (id))

    def get_state_info_str(self) -> list[str]:
        return self.state.summary()
