from collections import defaultdict
from typing import Any

import cv2
import numpy as np
from numpy.typing import NDArray

from coviso.utils.detect import set_base_detect
from coviso.utils.ops import coord_sorted, get_degree

from .base import Tracker


class LineTracker(Tracker):
    def __init__(self, cfg: dict[str, Any]) -> None:
        """
        Args:
            cfg (dict): Dictionary of process configuration parameters.
        """
        self.setup(cfg)
        self.line_statu_names = ["in", "out"]

    def line_shift(
        self, line: Any, size: tuple[int, int], factor: int = 25
    ) -> dict[str, list[int]]:
        """
        Args:
            line (Any): Coordinates of the specified lines.
            size (tuple): The size of the video frame.
            factor (int): The width factor of the line.
        Returns:
            dict: Dictionary containing line information.
        """
        (sx, sy), (fx, fy) = line[1], line[2]
        degree = get_degree(sx, sy, fx, fy)
        radi = np.radians(degree)
        c, s = np.cos(radi), np.sin(radi)

        line_dict = defaultdict(list)
        back = True

        for i in range(2):
            for point in line[:2]:
                if back:
                    point += np.array([c, -s]) * np.linalg.norm(np.array(size) / factor)
                else:
                    point -= np.array([c, -s]) * np.linalg.norm(np.array(size) / factor)

                line_dict[str(i)].append(point.astype(np.int32))
            line_dict[str(i)].append(line[1])
            line_dict[str(i)].append(line[0])
            back = False

        return line_dict

    def create_mask(self, size: tuple[int, int]) -> None:
        """
        Args:
            size (tuple): The dimensions of the processed video frame.
        """
        self.size = size
        self.mask = np.zeros(size)
        for i, name in enumerate(self.lines):
            line = self.lines[name]["line"]
            plines = self.line_shift(line, self.size)
            self.lines[name][f"areas"] = []
            for j, pline in enumerate(plines.values(), start=1):
                pline = coord_sorted(points=np.array(pline))
                color = i * len(plines) + j
                self.lines[name][f"areas"].append([color, pline])
                self.lines_info[str(color)] = name, self.line_statu_names[j - 1]
                cv2.fillPoly(img=self.mask, pts=[np.array(pline)], color=color)

    def setup(self, cfg: dict[str, Any]) -> None:
        """
        Args:
            cfg (dict): Dictionary of process configuration parameters.
        """
        self.cfg = cfg
        self.lines = self.set_lines(self.cfg)
        self.lines_info = {}
        self.tracked_info = defaultdict(dict)

    def set_lines(self, cfg: dict[str, Any]) -> dict[str, Any]:
        """
        Args:
            cfg (dict): Dictionary of process configuration parameters.
        Returns:
            dict: Dictionary containing area information.
        """
        lines = defaultdict(dict)
        for name, line in self.cfg["polys"].items():
            lines[name]["line"] = line
            lines[name]["in"] = 0
            lines[name]["out"] = 0
        return lines

    def draw_result(self, frame: NDArray[Any], result: Any) -> NDArray[Any]:
        """
        Args:
            frame (NDArray): The image of the video frame.
            result (Any): The output results from the model.
        Returns:
            NDArray: The image of the processed video frame.
        """
        for res in result:
            x1, y1, x2, y2 = res[:4].astype(int)
            cv2.rectangle(
                img=frame, pt1=(x1, y1), pt2=(x2, y2), color=(0, 0, 0), thickness=1
            )
            x, y = set_base_detect(np.array([x1, y1, x2, y2]), self.size)
            cv2.circle(
                img=frame,
                center=(int(x), int(y)),
                radius=5,
                color=(255, 255, 255),
                thickness=-1,
            )

            track_id = str(res[4].astype(np.int32))
            cls = str(res[6].astype(np.int32))

            cv2.putText(
                img=frame,
                text=f"Id: {track_id} - Cls: {cls}",
                org=(x1, y1 - 10),
                fontFace=1,
                fontScale=1,
                color=(255, 255, 255),
            )
        return frame

    def draw_lines(self, frame: NDArray[Any], lines: dict[str, Any]) -> NDArray[Any]:
        """
        Args:
            frame (NDArray): The image of the video frame.
            lines (dict): Dictionary containing line information.
        Returns:
            NDArray: The image of the processed video frame.
        """
        for name in lines.keys():
            for area, statu_name in zip(
                self.lines[name]["areas"], self.line_statu_names
            ):
                cv2.polylines(
                    img=frame,
                    pts=[np.array(area[1])],
                    isClosed=True,
                    color=(0, 0, 255),
                    thickness=2,
                )

                statu_num = self.lines[name][statu_name]

                cv2.putText(
                    img=frame,
                    text=f"{statu_name.capitalize()}: {statu_num} ",
                    org=area[1][0] + 20,
                    fontFace=1,
                    fontScale=1,
                    color=255,
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
        frame = self.draw_lines(frame, self.lines)
        return frame

    def check_line_statu(self, track_id: str, statu: int) -> None:

        (line_name, line_statu) = self.lines_info.get(str(statu), [None, None])

        if statu > 0 and self.tracked_info[track_id].get("Passed", None) is None:
            self.tracked_info[track_id]["Passed"] = False
            self.tracked_info[track_id]["entr_location"] = line_statu
            self.tracked_info[track_id]["last_location"] = line_statu
            self.tracked_info[track_id]["line_name"] = line_name

        if statu == 0:
            if self.tracked_info[track_id].get("Passed", None):
                line_name = self.tracked_info[track_id]["line_name"]
                line_statu = self.tracked_info[track_id]["entr_location"]
                self.lines[line_name][line_statu] += 1
            self.tracked_info[track_id] = {}
        else:

            if (
                self.tracked_info[track_id]["last_location"] == "in"
                and line_statu == "out"
            ):
                self.tracked_info[track_id]["Passed"] = True
            elif (
                self.tracked_info[track_id]["last_location"] == "out"
                and line_statu == "in"
            ):
                self.tracked_info[track_id]["Passed"] = True
            elif self.tracked_info[track_id]["entr_location"] == line_statu:
                self.tracked_info[track_id]["Passed"] = False

            self.tracked_info[track_id]["last_location"] = line_statu

    def compute(self, result: Any) -> dict[str, Any]:
        """
        Args:
            result (Any): The output results from the model.
        """
        for res in result:
            track_id = str(res[4].astype(np.int32))
            x, y = set_base_detect(xyxy=res[:4], size=self.size)
            statu = int(self.mask[y, x])
            self.check_line_statu(track_id=track_id, statu=statu)

        return self.lines

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

        return frame, self.lines
