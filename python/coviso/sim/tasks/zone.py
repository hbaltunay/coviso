import logging
from dataclasses import dataclass

import cv2
import numpy as np

from coviso.detect import Detection
from coviso.sim.core.agent import Agent, AgentInfo
from coviso.sim.core.rng import Rng
from coviso.sim.tasks.base import AgentData, CoordinateData, Task, TaskData
from coviso.sim.tasks.physics import MoveData, Movement

LOGGER = logging.getLogger("coviso")


@dataclass
class AgentZData(AgentData):
    rng: Rng = Rng(0, 0)
    move_data: MoveData | None = None
    target_zone: int = 0
    current_zone: int = 0


class ZoneTask(Task):
    def __init__(self) -> None:
        super().__init__()
        self.zones: CoordinateData = {}
        self.mask: np.ndarray = np.empty(0)
        self.coordinate_mask: dict = {}
        self.zone_list: list = []
        self.zone_num: int = 0
        self.zone_info: dict[int, int] = {}

    def get_zone_value(self, coord: tuple) -> int:
        return int(self.mask[int(coord[1]), int(coord[0])])

    def assign_random_target(self, agent_data: AgentZData) -> None:
        target_num = agent_data.rng.uniform_int(0, len(self.zones))
        if target_num == 0:
            target_coord = [
                float(agent_data.rng.uniform_int(0, self.imgsz[0] - 1)),
                float(agent_data.rng.uniform_int(0, self.imgsz[1] - 1)),
            ]
            agent_data.move_data.target_coord = target_coord
        else:
            target_coord_num = agent_data.rng.uniform_int(
                0, len(self.coordinate_mask[target_num]) - 1
            )
            target_coord = self.coordinate_mask[target_num][target_coord_num][0]
            agent_data.move_data.target_coord = target_coord

        agent_data.target_zone = self.get_zone_value(target_coord)
        agent_data.move_data.arrived = False

    def init(self, task_data: TaskData) -> bool:
        self.imgsz = task_data.imgsz
        self.zones = task_data.coor_data
        max_speed = max(self.imgsz[0], self.imgsz[1]) / (task_data.fps * 10.0)

        if not self.create_mask():
            return False

        for i in range(task_data.agent_num):
            name_agent = "Agent_Zone_" + str(i + 1)

            agent_data = AgentZData()
            agent_data.move_data = MoveData()
            agent_data.move_data.max_speed = max_speed
            agent_data.move_data.max_acceleration = 0.2
            agent_data.rng = Rng(task_data.seed, i)

            agent_data.move_data.current_coord = [
                float(agent_data.rng.uniform_int(0, self.imgsz[0] - 1)),
                float(agent_data.rng.uniform_int(0, self.imgsz[1] - 1)),
            ]

            self.assign_random_target(agent_data)
            self.add_agent(Agent(name_agent, i + 1, self))
            self.add_agent_data(name_agent, agent_data)

        return True

    def create_mask(self) -> bool:
        self.mask = np.zeros((self.imgsz[1], self.imgsz[0]), dtype=np.uint8)

        zone_id = 1
        max_zone_id = 255

        for zone_name, zone_map in self.zones.items():
            if "zone" not in zone_map:
                continue

            zone_points_raw = zone_map["zone"]
            zone_points = []

            for pt in zone_points_raw:
                if (
                    len(pt) == 2
                    and pt[0] >= 0
                    and pt[0] < self.imgsz[0]
                    and pt[1] >= 0
                    and pt[1] < self.imgsz[1]
                ):
                    zone_points.append(pt)

            if len(zone_points) < 3:
                continue

            current_zone = [np.array(zone_points, dtype=np.int32)]
            cv2.fillPoly(self.mask, current_zone, zone_id)

            zone_mask = np.zeros_like(self.mask, self.mask.dtype)
            cv2.fillPoly(zone_mask, current_zone, zone_id)

            exact_value_mask = cv2.compare(zone_mask, zone_id, cv2.CMP_EQ)

            inner_mask = cv2.erode(exact_value_mask, None)

            target_coordinates = cv2.findNonZero(inner_mask)
            self.coordinate_mask[zone_id] = target_coordinates
            self.zone_info[zone_id] = 0
            self.zone_list.append([zone_name, current_zone])

            zone_id += 1

            if zone_id > max_zone_id:
                LOGGER.warn("Zone limit reached!")
                return True

        self.zone_info[0] = 0
        self.zone_num = zone_id

        return True

    def generate(self) -> list[Detection]:
        detection_list: list[Detection] = []
        self.zone_info.update(dict.fromkeys(self.zone_info, 0))

        for agent in self.get_agents():
            detection: Detection = agent.run()
            detection_list.append(detection)

        return detection_list

    def calculate(self, agent_info: AgentInfo) -> None:
        d: AgentZData = self.get_agent_data(agent_info.name)

        if d.move_data.arrived:
            self.assign_random_target(d)

        Movement.move(d.move_data)

        d.current_zone = self.get_zone_value(d.move_data.current_coord)

        self.zone_info[d.current_zone] += 1

        agent_info.detection.bbox.x = d.move_data.current_coord[0]
        agent_info.detection.bbox.y = d.move_data.current_coord[1]

    def draw_canvas(self, canvas: np.ndarray) -> None:
        for _, zone in self.zone_list:
            cv2.fillPoly(canvas, zone, (128, 128, 128))

    def draw_canvas_status(self, canvas: np.ndarray) -> None:
        start_x = 15
        start_y = 30
        line_spacing = 25

        for zone_id in range(self.zone_num):
            count = self.zone_info[zone_id]
            text = "Zone " + str(zone_id) + ": " + str(count)

            cv2.putText(
                canvas,
                text,
                (start_x, start_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

            start_y += line_spacing

    def get_poly_num(self) -> int:
        return self.zone_num
