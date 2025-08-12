from typing import Any

from .ops import xyxy2xywh


def set_base_detect(xyxy: Any, size: Any) -> tuple[int, int]:
    x, y, _, h = xyxy2xywh(xyxy)
    return (int(x), min(int(y + h / 2), size[0]) - 1)
