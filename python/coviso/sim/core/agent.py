from dataclasses import dataclass

from coviso.detect import Detection


@dataclass
class AgentInfo:
    agent_id: int
    name: str = ""
    detection: Detection | None = None

    def __post_init__(self) -> None:
        self.detection = Detection()


class Task:
    pass


class Agent:
    def __init__(self, name: str, agent_id: int, task: Task) -> None:
        self.name = name
        self.agent_id = agent_id
        self.task = task
        self.agent_info = AgentInfo(agent_id=self.agent_id, name=self.name)
        self.agent_info.detection.track_id = self.agent_id

    def run(self) -> Detection:
        self.task.calculate(self.agent_info)
        return self.agent_info.detection
