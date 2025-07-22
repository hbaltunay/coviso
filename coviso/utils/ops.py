from typing import Any

from numpy.typing import NDArray


def xywh2xyxy(xywh: NDArray[Any]) -> Any:
    x, y, w, h = xywh
    return x - w / 2, y - h / 2, x + w / 2, y + h / 2


def xyxy2xywh(xyxy: NDArray[Any]) -> Any:
    x1, y1, x2, y2 = xyxy
    x, y = (x2 + x1) / 2, (y2 + y1) / 2
    w, h = (x2 - x1), (y2 - y1)
    return x, y, w, h
