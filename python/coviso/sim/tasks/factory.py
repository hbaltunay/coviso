from typing import TYPE_CHECKING, Any

from coviso.sim.tasks.line import LineTask
from coviso.sim.tasks.zone import ZoneTask

if TYPE_CHECKING:
    from collections.abc import Callable


class TaskFactory:
    _instance: "TaskFactory | None" = None

    def __new__(cls) -> "TaskFactory":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_factory()
        return cls._instance

    def _init_factory(self) -> None:
        self._tasks: dict[str, Callable[[], Any]] = {
            "Zone": ZoneTask,
            "Line": LineTask,
        }

    @classmethod
    def get_instance(cls) -> "TaskFactory":
        return cls()

    def create_task(self, task_name: str) -> Any | None:
        task_class = self._tasks.get(task_name)
        if task_class:
            return task_class()
        return None
