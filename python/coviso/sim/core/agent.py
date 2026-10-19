from dataclasses import dataclass

from coviso.detect import Detection


@dataclass
class AgentInfo:
    id: int
    name: str = ""
    detection: Detection | None = None

    def __post_init__(self) -> None:
        self.detection = Detection()


class Task:
    pass


class Agent:
    def __init__(self, name: str, id: int, task: Task) -> None:
        self.name = name
        self.id = id
        self.task = task
        self.agent_info = AgentInfo(id=self.id, name=self.name)

    def run(self) -> Detection:
        self.task.calculate(self.agent_info)
        return self.agent_info.detection
