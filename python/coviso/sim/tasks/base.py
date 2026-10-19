from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np

from coviso.detect import Detection
from coviso.sim import Agent, AgentInfo

type Coordinate2D = list[int]
type CoordinateList = list[Coordinate2D]
type InnerMap = dict[str, CoordinateList]
type CoordinateData = dict[str, InnerMap]


@dataclass
class TaskData:
    agent_num: int
    seed: int
    fps: int
    imgsz: tuple[int, int]
    coor_data: CoordinateData


class AgentData:
    pass


class Task(ABC):
    def __init__(self) -> None:
        self.seed_: int = 0
        self.imgsz: list = []
        self.agents: list = []
        self.agent_data: dict[str, AgentData] = {}

    @abstractmethod
    def init(self, task_data: TaskData) -> bool:
        pass

    @abstractmethod
    def generate(self) -> list[Detection]:
        pass

    @abstractmethod
    def calculate(self, agent_info: AgentInfo) -> None:
        pass

    def add_agent(self, agent: Agent) -> None:
        self.agents.append(agent)

    def get_agents(self) -> list[Agent]:
        return self.agents

    @abstractmethod
    def draw_canvas(self, canvas: np.ndarray) -> None:
        pass

    @abstractmethod
    def draw_canvas_status(self, canvas: np.ndarray) -> None:
        pass

    def add_agent_data(self, name: str, data: AgentData) -> None:
        self.agent_data[name] = data

    def get_agent_data(self, name: str) -> AgentData:
        return self.agent_data[name]

    def get_agent_map(self) -> dict[str, AgentData]:
        return self.agent_data

    @abstractmethod
    def get_poly_num(self) -> int:
        pass
