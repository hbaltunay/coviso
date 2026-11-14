from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import cv2
import numpy as np


class State(ABC):
    def __init__(self, imgsz: tuple[int]) -> None:
        self.imgsz = imgsz

    @abstractmethod
    def add(self, info_id: int, poly: list) -> bool:
        pass

    @abstractmethod
    def remove(self, info_id: int) -> bool:
        pass

    @abstractmethod
    def summary(self) -> list[str]:
        pass


@dataclass
class ZoneInfo:
    info_id: int
    num: int
    in_zone: list
    empty: bool


@dataclass
class ZoneDrawInfo:
    info_id: int
    num: int
    zone: list
    in_zone: list
    empty: bool
    mask: np.ndarray | None = None
    mask_roi: np.ndarray = field(init=False)
    mask_roi_u8: np.ndarray = field(init=False)
    one_roi: np.ndarray = field(init=False)
    zero_roi: np.ndarray = field(init=False)
    blended: np.ndarray = field(init=False)
    roi: tuple = field(init=False)

    def __post_init__(self) -> None:
        if self.mask is None:
            return

        ys, xs = np.where(self.mask)
        self.roi = (
            slice(ys.min(), ys.max() + 1),
            slice(xs.min(), xs.max() + 1),
        )

        self.mask_roi = self.mask[self.roi][..., None]
        self.mask_roi_u8 = np.ascontiguousarray(
            self.mask[self.roi].astype(np.uint8) * 255
        )

        h, w = self.mask_roi.shape[:2]
        self.one_roi = np.zeros((h, w, 3), dtype=np.uint8)
        self.one_roi[:] = (0, 0, 255)

        self.zero_roi = np.zeros((h, w, 3), dtype=np.uint8)
        self.zero_roi[:] = (0, 255, 0)

        self.blended = np.empty_like(self.one_roi)


class ZoneState(State):
    def __init__(self, imgsz: tuple[int]) -> None:
        super().__init__(imgsz)
        self.zone_infos: dict[int, ZoneInfo] = {}
        self.zone_draw_infos: dict[int, ZoneDrawInfo] = {}

    def add(self, info_id: int, poly: list) -> bool:
        if info_id > 0:
            mask0 = np.zeros((self.imgsz[1], self.imgsz[0]), dtype=np.uint8)
            current_zone = [np.array(poly, dtype=np.int32)]
            cv2.fillPoly(mask0, current_zone, info_id)
            mask = mask0 == info_id
        else:
            mask = None

        zone_info = ZoneInfo(info_id, 0, [], False)
        zone_draw_info = ZoneDrawInfo(info_id, 0, poly, [], False, mask)
        self.zone_infos[info_id] = zone_info
        self.zone_draw_infos[info_id] = zone_draw_info
        return True

    def remove(self, info_id: int) -> bool:
        return True  # TODO

    def summary(self) -> list[str]:
        str_infos = []
        for i in range(len(self.zone_infos)):
            zone_info = self.zone_infos[i]
            str_info = (
                "[ Zone-" + str(zone_info.info_id) + " ] :" + str(zone_info.num)
            )
            str_infos.append(str_info)
        return str_infos

    def update_plain(self, zone_freq: dict[int, int]) -> bool:
        """
        Zone monitoring method without object tracking.
        """
        for i in range(len(self.zone_infos)):
            self.zone_infos[i].num = zone_freq[i]
            self.zone_infos[i].empty = self.zone_infos[i].num == 0
        return True

    def update_tracked(self, zone_in: dict[int, list]) -> bool:
        """
        Zone monitoring method with object tracking.
        """
        for i in range(len(self.zone_infos)):
            self.zone_infos[i].num = len(zone_in[i])
            self.zone_infos[i].empty = self.zone_infos[i].num == 0
        return True

    def draw(self, image: np.ndarray) -> None:
        for zone_id, zone in self.zone_draw_infos.items():
            if zone_id == 0:
                continue

            roi = image[zone.roi]
            overlay = (
                zone.zero_roi
                if self.zone_infos[zone_id].empty
                else zone.one_roi
            )
            cv2.addWeighted(roi, 0.4, overlay, 0.6, 0, zone.blended)
            cv2.copyTo(zone.blended, zone.mask_roi_u8, roi)


@dataclass
class TrackInfo:
    current_line: int = 0
    last_line: int = 0
    passed: bool = False
    passed_num: int = 0


@dataclass
class LineInfo:
    info_id: int
    count: int
    line_num: int
    line_type: str


@dataclass
class LineDrawInfo:
    info_id: int
    count: int
    line_num: int
    line_type: str
    line: list
    mask: np.ndarray | None = None
    mask_roi: np.ndarray = field(init=False)
    mask_roi_u8: np.ndarray = field(init=False)
    line_roi: np.ndarray = field(init=False)
    blended: np.ndarray = field(init=False)
    roi: tuple = field(init=False)

    def __post_init__(self) -> None:
        if self.mask is None:
            return

        ys, xs = np.where(self.mask)
        self.roi = (
            slice(ys.min(), ys.max() + 1),
            slice(xs.min(), xs.max() + 1),
        )

        self.mask_roi = self.mask[self.roi][..., None]
        self.mask_roi_u8 = np.ascontiguousarray(
            self.mask[self.roi].astype(np.uint8) * 255
        )

        h, w = self.mask_roi.shape[:2]
        if self.line_type == "entry":
            self.line_roi = np.zeros((h, w, 3), dtype=np.uint8)
            self.line_roi[:] = (0, 255, 0)
        else:
            self.line_roi = np.zeros((h, w, 3), dtype=np.uint8)
            self.line_roi[:] = (0, 0, 255)

        self.blended = np.empty_like(self.line_roi)


class LineState(State):
    def __init__(self, imgsz: tuple[int]) -> None:
        super().__init__(imgsz)
        self.line_infos: dict[int, LineInfo] = {}
        self.track_infos: dict[int, TrackInfo] = {}
        self.line_draw_infos: dict[int, LineDrawInfo] = {}

    def add(self, info_id: int, poly: list) -> bool:
        line_type, line_num = (
            ("entry", info_id + 1)
            if (info_id % 2 == 1)
            else ("exit", info_id - 1)
        )

        mask0 = np.zeros((self.imgsz[1], self.imgsz[0]), dtype=np.uint8)
        current_zone = [np.array(poly, dtype=np.int32)]
        cv2.fillPoly(mask0, current_zone, info_id)
        mask = mask0 == info_id

        line_info = LineInfo(info_id, 0, line_num, line_type)
        line_draw_info = LineDrawInfo(
            info_id, 0, line_num, line_type, poly, mask
        )
        self.line_infos[info_id] = line_info
        self.line_draw_infos[info_id] = line_draw_info
        return True

    def remove(self, info_id: int) -> bool:
        return True  # TODO

    def summary(self) -> list[str]:
        str_infos = []
        for i in range(len(self.line_infos)):
            line_info = self.line_infos[i + 1]
            str_info = (
                "[ Line-"
                + str(line_info.info_id)
                + "-"
                + line_info.line_type
                + " ] :"
                + str(line_info.count)
            )
            str_infos.append(str_info)

        return str_infos

    def update(self) -> bool:
        return True

    def draw(self, image: np.ndarray) -> None:
        for line in self.line_draw_infos.values():
            roi = image[line.roi]
            cv2.addWeighted(roi, 0.4, line.line_roi, 0.6, 0, line.blended)
            cv2.copyTo(line.blended, line.mask_roi_u8, roi)
