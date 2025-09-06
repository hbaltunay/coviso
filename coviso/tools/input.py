from collections import defaultdict
from typing import Any

import cv2
import numpy as np
from numpy.typing import NDArray

from ..loggers import CLogger

logger = CLogger(__name__)


class AnyInput:
    def __init__(self):
        pass

    def get_first_frame(self, source_path: str):
        cap = cv2.VideoCapture(source_path)
        _, self.frame = cap.read()
        cap.release()
        return self.frame

    def set_callback(self, frame: NDArray[Any], onMouse: Any):
        cv2.imshow("Coviso", frame)
        cv2.setMouseCallback("Coviso", onMouse)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


class VideoAreaInput(AnyInput):
    def __init__(self, num: int):
        self.num = num
        self.area = []
        self.areas = defaultdict(list)
        self.last_num = 0

    def draw_areas(self, sing_areas: Any):

        areas = [*self.areas.values()]

        if sing_areas != []:
            areas.append(sing_areas)

        for area in areas:
            cv2.polylines(
                img=self.processed_frame,
                pts=[np.array([area])],
                isClosed=True,
                color=(255, 0, 0),
                thickness=2,
            )

            for x, y in area:
                self.processed_frame = cv2.circle(
                    img=self.processed_frame,
                    center=(x, y),
                    radius=3,
                    color=(0, 255, 0),
                    thickness=-1,
                )

        cv2.putText(
            img=self.processed_frame,
            text="L: Next - R: Undo - CTRL+L: Save - CTRL+R: Del - Press Q to save and exit.",
            org=(25, self.frame.shape[0] - 25),
            fontFace=1,
            fontScale=2,
            color=(0, 0, 255),
            thickness=2,
        )

    def click_event(self, event: int, x: int, y: int, flags: int, params: Any):
        if event == cv2.EVENT_LBUTTONUP and flags == cv2.EVENT_FLAG_CTRLKEY:
            if self.area and len(self.area) == self.num:
                self.last_num += 1
                self.areas[f"area_{self.last_num}"] = self.area
                self.area = []

        elif event == cv2.EVENT_RBUTTONUP and flags == cv2.EVENT_FLAG_CTRLKEY:
            if self.areas:
                self.areas.pop(f"area_{self.last_num}")
                self.processed_frame = self.frame.copy()
                self.last_num -= 1

        elif event == cv2.EVENT_LBUTTONUP:
            self.area.append((x, y))
            self.processed_frame = self.frame.copy()

        elif event == cv2.EVENT_RBUTTONUP:
            if self.area:
                self.area.pop()
            self.processed_frame = self.frame.copy()

        if event:
            self.draw_areas(self.area)

        cv2.imshow("Coviso", self.processed_frame)

    def process(self, cfg_dict: dict[str, Any]) -> dict[str, Any]:
        source_path = cfg_dict.get("source_path", None)

        if source_path is None:
            raise FileNotFoundError("Video source not found.")
        else:
            self.frame = self.get_first_frame(source_path)

        areas = cfg_dict.get("areas", None)
        if areas is not None:
            self.areas.update(areas)
            self.last_num = len(self.areas)
        self.processed_frame = self.frame.copy()

        self.draw_areas([])

        self.set_callback(self.frame, self.click_event)

        return {"areas": dict(self.areas)}


class VideoLineInput(AnyInput):
    def __init__(self, num: int):
        self.num = num
        self.line = []
        self.lines = defaultdict(list)
        self.last_num = 0

    def draw_lines(self, sing_line: Any):
        lines = [*self.lines.values()]
        if sing_line != []:
            lines.append(sing_line)

        for line in lines:
            if len(line) == 3:
                for i in range(2):
                    cv2.line(
                        img=self.processed_frame,
                        pt1=line[i],
                        pt2=line[i + 1],
                        color=255,
                        thickness=2,
                    )
            elif len(line) == 2:
                cv2.line(
                    img=self.processed_frame,
                    pt1=line[0],
                    pt2=line[1],
                    color=255,
                    thickness=2,
                )

            for x, y in line:
                self.processed_frame = cv2.circle(
                    img=self.processed_frame,
                    center=(x, y),
                    radius=3,
                    color=255,
                    thickness=-1,
                )

        cv2.putText(
            img=self.processed_frame,
            text="L: Next - R: Undo - CTRL+L: Save - CTRL+R: Del - Press Q to save and exit.",
            org=(25, self.frame.shape[0] - 25),
            fontFace=1,
            fontScale=2,
            color=(0, 0, 255),
            thickness=2,
        )

    def click_event(self, event: int, x: int, y: int, flags: int, params: Any):
        if event == cv2.EVENT_LBUTTONUP and flags == cv2.EVENT_FLAG_CTRLKEY:
            if self.line and len(self.line) == self.num:
                self.last_num += 1
                self.lines[f"line_{self.last_num}"] = self.line
                self.line = []

        elif event == cv2.EVENT_RBUTTONUP and flags == cv2.EVENT_FLAG_CTRLKEY:
            if self.lines:
                self.lines.pop(f"line_{self.last_num}")
                self.processed_frame = self.frame.copy()
                self.last_num -= 1

        elif event == cv2.EVENT_LBUTTONUP:
            self.line.append((x, y))
            self.processed_frame = self.frame.copy()

        elif event == cv2.EVENT_RBUTTONUP:
            if self.line:
                self.line.pop()
            self.processed_frame = self.frame.copy()

        self.line = self.line[-self.num:]

        if event or flags:
            self.draw_lines(self.line)

        cv2.imshow("Coviso", self.processed_frame)

    def process(self, cfg_dict: dict[str, Any]) -> dict[str, Any]:
        source_path = cfg_dict.get("source_path", None)

        if source_path is None:
            raise FileNotFoundError("Video source not found.")
        else:
            self.frame = self.get_first_frame(source_path)

        lines = cfg_dict.get("polys", None)
        if lines is not None:
            self.lines.update(lines)
            self.last_num = len(self.lines)
        self.processed_frame = self.frame.copy()

        self.draw_lines([])

        self.set_callback(self.frame, self.click_event)

        return {"lines": dict(self.lines)}
