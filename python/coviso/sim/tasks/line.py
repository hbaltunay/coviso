import logging
import math
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
class LineInfoData:
    name: str
    first_point: list[int]
    second_point: list[int]
    width: float
    angle: float
    entry_zone: list[int]
    exit_zone: list[int]


@dataclass
class LineData:
    name: str
    line: list[int]


@dataclass
class LinePassedInfo:
    line_name: str
    line_type: str
    line_num: int
    count: int


@dataclass
class AgentLData(AgentData):
    rng: Rng = Rng(0, 0)
    move_data: MoveData | None = None
    target_line: int = 0
    current_line: int = 0
    last_line: int = 0
    passed: bool = False
    passed_num: int = 0


class LineTask(Task):
    def __init__(self) -> None:
        super().__init__()
        self.lines: CoordinateData = {}
        self.coordinate_mask: dict = {}
        self.line_list: list = []
        self.line_info_list: list[LineInfoData] = []
        self.line_info: dict[str, LinePassedInfo] = {}

    def get_line_value(self, coord: tuple) -> int:
        return int(self.mask[int(coord[1]), int(coord[0])])

    def assign_random_target(self, agent_data: AgentLData) -> None:
        target_num = agent_data.rng.uniform_int(0, len(self.lines))
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

        agent_data.target_line = self.get_line_value(target_coord)
        agent_data.move_data.arrived = False

    def init(self, task_data: TaskData) -> bool:
        self.imgsz = task_data.imgsz
        self.lines = task_data.coor_data
        max_speed = max(self.imgsz[0], self.imgsz[1]) / (task_data.fps * 10.0)

        if not self.create_mask():
            return False

        for i in range(task_data.agent_num):
            name_agent = "Agent_Line_" + str(i + 1)

            agent_data = AgentLData()
            agent_data.move_data = MoveData()
            agent_data.move_data.max_speed = max_speed
            agent_data.move_data.max_acceleration = 0.2
            agent_data.rng = Rng(task_data.seed, i)

            agent_data.move_data.current_coord = [
                float(agent_data.rng.uniform_int(0, self.imgsz[0] - 1)),
                float(agent_data.rng.uniform_int(0, self.imgsz[1] - 1)),
            ]
            agent_data.move_data.last_line = agent_data.move_data.current_coord

            self.assign_random_target(agent_data)
            self.add_agent(Agent(name_agent, i + 1, self))
            self.add_agent_data(name_agent, agent_data)

        return True

    def create_line_zones(
        self,
        first_point: list[int],
        second_point: list[int],
        width: float,
        angle: float,
    ) -> list:
        x1, y1 = first_point
        x2, y2 = second_point

        dx = float(x2 - x1)
        dy = float(y2 - y1)
        line_length = math.sqrt(dx * dx + dy * dy)

        if line_length < 0.001:
            return []

        base_angle_rad = math.atan2(dy, dx)

        offset_angle_rad = (angle * math.pi) / 180.0
        final_angle_rad = base_angle_rad + offset_angle_rad

        shift_x = width * math.cos(final_angle_rad)
        shift_y = width * math.sin(final_angle_rad)

        line_entry = np.array(
            [
                [x1, y1],
                [x2, y2],
                [int(x2 + shift_x), int(y2 + shift_y)],
                [int(x1 + shift_x), int(y1 + shift_y)],
            ],
            dtype=np.int32,
        )

        line_exit = np.array(
            [
                [x1, y1],
                [x2, y2],
                [int(x2 - shift_x), int(y2 - shift_y)],
                [int(x1 - shift_x), int(y1 - shift_y)],
            ],
            dtype=np.int32,
        )

        return [line_entry, line_exit]

    def create_mask(self) -> bool:
        self.mask = np.zeros((self.imgsz[1], self.imgsz[0]), dtype=np.uint8)

        line_id = 1
        max_line_id = 254

        for line_name, line_map in self.lines.items():
            if "line" not in line_map:
                continue

            line_points_raw = line_map["line"]
            line_points = []

            w = 0
            a = 0
            first_point = [0.0, 0.0]
            second_point = [0.0, 0.0]

            for i in range(3):
                pt = line_points_raw[i]
                if i < 2:
                    if (
                        len(pt) == 2
                        and pt[0] >= 0
                        and pt[0] < self.imgsz[0]
                        and pt[1] >= 0
                        and pt[1] < self.imgsz[1]
                    ):
                        line_points.append(pt)

                        if i == 0:
                            first_point = pt
                        else:
                            second_point = pt
                else:
                    if (
                        len(pt) == 2
                        and pt[0] >= 0
                        and pt[0] < max(self.imgsz)
                        and pt[1] >= 45
                        and pt[1] <= 135
                    ):
                        line_points.append(pt)
                        w = pt[0]
                        a = pt[1]

            if len(line_points) != 3:
                continue

            line_zones = self.create_line_zones(first_point, second_point, w, a)

            for line_zone in line_zones:
                current_zone = [np.array(line_zone, dtype=np.int32)]
                cv2.fillPoly(self.mask, current_zone, line_id)

                zone_mask = np.zeros_like(self.mask, self.mask.dtype)
                cv2.fillPoly(zone_mask, current_zone, line_id)

                exact_value_mask = cv2.compare(zone_mask, line_id, cv2.CMP_EQ)

                inner_mask = cv2.erode(exact_value_mask, None)

                target_coordinates = cv2.findNonZero(inner_mask)
                self.coordinate_mask[line_id] = target_coordinates

                line_id += 1

            self.line_info_list.append(
                LineInfoData(
                    name=line_name,
                    first_point=first_point,
                    second_point=second_point,
                    width=w,
                    angle=a,
                    entry_zone=line_zones[0],
                    exit_zone=line_zones[1],
                )
            )

            self.line_list.append(LineData(line_name + "_entry", line_zones[0]))
            self.line_list.append(LineData(line_name + "_exit", line_zones[1]))

            self.line_info[line_id - 2] = LinePassedInfo(
                line_name, "entry", line_id - 1, 0
            )
            self.line_info[line_id - 1] = LinePassedInfo(
                line_name, "exit", line_id - 2, 0
            )

            if line_id > max_line_id:
                LOGGER.warn("Line limit reached!")
                return True

        self.line_num = line_id

        return True

    def generate(self) -> list[Detection]:
        detection_list: list[Detection] = []

        for agent in self.get_agents():
            detection: Detection = agent.run()
            detection_list.append(detection)

        return detection_list

    def calculate(self, agent_info: AgentInfo) -> None:
        d: AgentLData = self.get_agent_data(agent_info.name)

        if d.move_data.arrived:
            self.assign_random_target(d)

        Movement.move(d.move_data)

        d.current_line = self.get_line_value(d.move_data.current_coord)

        if d.current_line != d.last_line:
            if d.passed_num == 0:
                d.passed_num = (
                    d.last_line if (d.last_line) > 0 else d.current_line
                )
            elif not d.passed and d.current_line == 0:
                d.passed_num = 0
            elif d.passed and d.current_line == 0:
                passed_line = self.line_info.get(d.last_line).line_num
                self.line_info.get(passed_line).count += 1
                d.passed = False
                d.passed_num = 0
            elif d.current_line == d.passed_num:
                d.passed = False
            elif d.last_line == self.line_info.get(d.current_line).line_num:
                d.passed = True
            else:
                print("Invalid action performed.")

        d.last_line = d.current_line

        agent_info.detection.id = agent_info.id
        agent_info.detection.bbox.x = d.move_data.current_coord[0]
        agent_info.detection.bbox.y = d.move_data.current_coord[1]

    def draw_canvas(self, canvas: np.ndarray) -> None:
        for line in self.line_info_list:
            cv2.fillPoly(canvas, [line.entry_zone], [1])
            cv2.fillPoly(canvas, [line.exit_zone], [2])

    def draw_canvas_status(self, canvas: np.ndarray) -> None:
        start_x = 15
        start_y = 30
        line_spacing = 25

        for line_id in range(0, len(self.line_info)):
            info = self.line_info[line_id + 1]
            text = (
                info.line_name + "-" + info.line_type + " : " + str(info.count)
            )

            cv2.putText(
                canvas,
                text,
                (start_x, start_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                [255],
                1,
                cv2.LINE_AA,
            )

            start_y += line_spacing

    def get_poly_num(self) -> int:
        return self.line_num
