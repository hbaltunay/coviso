from typing import Any

import numpy as np
from numpy.typing import NDArray


def xywh2xyxy(xywh: NDArray[Any]) -> NDArray[Any]:
    x, y, w, h = xywh
    return np.array([x - w / 2, y - h / 2, x + w / 2, y + h / 2])


def xyxy2xywh(xyxy: NDArray[Any]) -> NDArray[Any]:
    x1, y1, x2, y2 = xyxy
    x, y = (x2 + x1) / 2, (y2 + y1) / 2
    w, h = (x2 - x1), (y2 - y1)
    return np.array([x, y, w, h])


def get_degree(sx: int, sy: int, fx: int, fy: int) -> int:
    degree = np.degrees(np.arctan2(fy - sy, fx - sx))
    if degree >= 0:
        return 360 - degree
    else:
        return -degree


def coord_sorted(points: NDArray[Any]) -> NDArray[Any]:
    ox, oy = np.mean(points, axis=0)
    angles = np.arctan2(points[:, 1] - oy, points[:, 0] - ox)
    sorted_indices = np.argsort(angles)
    return points[sorted_indices]
