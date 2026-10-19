from abc import ABC, abstractmethod
from dataclasses import dataclass


class State(ABC):
    @abstractmethod
    def add(self, id: int, poly: list) -> bool:
        pass

    @abstractmethod
    def remove(self, id: int) -> bool:
        pass

    @abstractmethod
    def summary(self) -> list[str]:
        pass


@dataclass
class ZoneInfo:
    id: int
    num: int
    zone: list
    in_zone: list


class ZoneState(State):
    def __init__(self) -> None:
        self.zone_infos: dict[int, ZoneInfo] = {}

    def add(self, id: int, poly: list) -> bool:
        zone_info = ZoneInfo(id, 0, poly, [])
        self.zone_infos[id] = zone_info
        return True

    def remove(self, id: int) -> bool:
        return True  # TODO

    def summary(self) -> list[str]:
        str_infos = []
        for i in range(len(self.zone_infos)):
            zone_info = self.zone_infos[i]
            str_info = (
                "[ Zone-" + str(zone_info.id) + " ] :" + str(zone_info.num)
            )
            str_infos.append(str_info)
        return str_infos

    def update_plain(self, zone_freq: dict[int, int]) -> bool:
        for i in range(len(self.zone_infos)):
            self.zone_infos[i].num = zone_freq[i]
        return True

    def update_tracked(self) -> bool:
        for i in range(len(self.zone_infos)):
            self.zone_infos[i].num = len(self.zone_infos[i].in_zone)
            self.zone_infos[i].in_zone.clear()
        return True


@dataclass
class TrackInfo:
    current_line: int = 0
    last_line: int = 0
    passed: bool = False
    passed_num: int = 0


@dataclass
class LineInfo:
    id: int
    count: int
    line_num: int
    line_type: str
    line: list


class LineState(State):
    def __init__(self) -> None:
        self.line_infos: dict[int, LineInfo] = {}
        self.track_infos: dict[int, TrackInfo] = {}

    def add(self, id: int, poly: list) -> bool:
        line_num, line_type = (
            (id + 1, "entry") if (id % 2 == 1) else (id - 1, "exit")
        )
        line_info = LineInfo(id, 0, line_num, line_type, poly)
        self.line_infos[id] = line_info
        return True

    def remove(self, id: int) -> bool:
        return True  # TODO

    def summary(self) -> list[str]:
        str_infos = []
        for i in range(len(self.line_infos)):
            line_info = self.line_infos[i + 1]
            str_info = (
                "[ Line-"
                + str(line_info.id)
                + "-"
                + line_info.line_type
                + " ] :"
                + str(line_info.count)
            )
            str_infos.append(str_info)

        return str_infos

    def update(self) -> bool:
        return True
