from collections import defaultdict
from typing import Any

import cv2
import numpy as np

from ..loggers import CLogger

logger = CLogger(__name__)


class VideoAreaInput:
    def __init__(self, num: int):
        self.num = num
        self.area = []
        self.areas = defaultdict(list)
        self.last_num = 0

    def get_first_frame(self, source_path: str):
        cap = cv2.VideoCapture(source_path)
        _, self.frame = cap.read()
        cap.release()
        return self.frame

    def draw_areas(self, sing_areas: Any):

        areas = [*self.areas.values()]
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
                    radius=5,
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

        cv2.imshow("Coviso", self.frame)
        cv2.setMouseCallback("Coviso", self.click_event)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        return {"areas": dict(self.areas)}
