from dataclasses import dataclass


@dataclass
class BBox:
    x: int = 0
    y: int = 0
    w: int = 0
    h: int = 0


@dataclass
class Detection:
    bbox: BBox | None = None
    class_id: int = 0
    track_id: int = 0

    def __post_init__(self) -> None:
        self.bbox = BBox()
