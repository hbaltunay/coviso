import logging
import time
from dataclasses import dataclass
from enum import Enum

LOGGER = logging.getLogger("coviso")


class Status(Enum):
    APPLIED = 0
    ACTIVE = 1
    LOST = 2
    REMOVE = 3


@dataclass
class EntityB:
    tid: int
    exist: int = 0
    location: int | None = None
    status: Status = Status.ACTIVE


class EntityBase:
    def __init__(self) -> None:
        self.applied_ids = set()
        self.entities: dict[int, EntityB] = {}

    def check(self, entity: EntityB) -> bool:
        if entity.status == Status.ACTIVE:
            entity.exist = 0
            return True

        entity.status = Status.LOST

        if entity.exist > self.zone_ctrl:
            entity.status = Status.REMOVE
            self.entities.pop(entity.tid)
            self.applied_ids.remove(entity.tid)

        entity.exist += 1

        return False


@dataclass
class EntityZ(EntityB):
    ctrl: int = 0
    current_location: int | None = None
    last_location: int | None = None
    entry_time: float | None = None
    exit_time: float | None = None


class EntityZone(EntityBase):
    def __init__(self, zone_ctrl: int = 90) -> None:
        super().__init__()
        self.zone_ctrl = zone_ctrl

    def add(self, tid: int, location: int) -> None:
        self.entities[tid] = EntityZ(
            tid=tid,
            location=location,
            last_location=location,
            entry_time=time.time(),
        )

    def update(self, tid: int, location: int) -> None:
        if tid not in self.applied_ids:
            self.add(tid, location)
            self.applied_ids.add(tid)
        else:
            self.entities[tid].current_location = location
            self.entities[tid].status = Status.ACTIVE

    def apply(self) -> None:
        for entity in self.entities.values():
            if not self.check(entity):
                continue

            if entity.last_location != entity.current_location:
                entity.ctrl = 0

            if entity.location != entity.current_location:
                if entity.ctrl > self.zone_ctrl:
                    entity.exit_time = time.time()
                    self.log(entity)
                    entity.location = entity.current_location
                    entity.entry_time = time.time()
                    entity.exit_time = None
                    entity.ctrl = 0
                entity.ctrl += 1

            entity.last_location = entity.current_location
            entity.status = Status.APPLIED

    def log(self, entity: EntityZ) -> None:
        LOGGER.info(
            f"Track Id: {str(entity.tid).ljust(5)} | "
            f"Location: {entity.location} | "
            f"Entry Time: {time.ctime(entity.entry_time)} | "
            f"Exit Time: {time.ctime(entity.exit_time)}"
        )


@dataclass
class EntityL(EntityB):
    passed_location: int = 0
    passed_time: float | None = None
    passed: bool = False


class EntityLine(EntityBase):
    def __init__(self, line_ctrl: int = 90) -> None:
        super().__init__()
        self.line_ctrl = line_ctrl

    def add(self, tid: int, location: int) -> None:
        self.entities[tid] = EntityL(
            tid=tid,
            location=location,
        )

    def update(self, tid: int, location: int) -> None:
        if tid not in self.applied_ids:
            self.add(tid, location)
            self.applied_ids.add(tid)
        else:
            self.entities[tid].location = location
            self.entities[tid].status = Status.ACTIVE

    def on_passed(self, tid: int, location: int) -> None:
        self.entities[tid].passed_location = location
        self.entities[tid].passed_time = time.time()
        self.entities[tid].passed = True

    def apply(self) -> None:
        for entity in self.entities.values():
            if not self.check(entity):
                continue

            if entity.passed:
                self.log(entity)
                entity.passed = False

            entity.status = Status.APPLIED

    def log(self, entity: EntityL) -> None:
        LOGGER.info(
            f"Track Id: {str(entity.tid).ljust(5)} | "
            f"Passed Line: {entity.passed_location} | "
            f"Passed Time: {time.ctime(entity.passed_time)}",
        )
