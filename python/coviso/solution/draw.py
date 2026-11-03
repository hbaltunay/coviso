import cv2
import numpy as np

from coviso.solution.state import LineInfo, ZoneInfo


def draw_zone(image: np.ndarray, zones: dict[int, ZoneInfo]) -> None:
    for zone_id, zone in zones.items():
        if zone_id == 0:
            continue

        roi = image[zone.roi]
        overlay = zone.zero_roi if zone.empty else zone.one_roi
        cv2.addWeighted(roi, 0.4, overlay, 0.6, 0, zone.blended)
        cv2.copyTo(zone.blended, zone.mask_roi_u8, roi)


def draw_line(image: np.ndarray, lines: dict[int, LineInfo]) -> None:
    for line in lines.values():
        roi = image[line.roi]
        cv2.addWeighted(roi, 0.4, line.line_roi, 0.6, 0, line.blended)
        cv2.copyTo(line.blended, line.mask_roi_u8, roi)
