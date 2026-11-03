from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

from coviso.detect import Detection
from coviso.sim.tasks.base import CoordinateData, Task, TaskData
from coviso.sim.tasks.factory import TaskFactory
from coviso.tool.config import Config


@dataclass
class TaskList:
    name: str
    task: Task


class Simulator:
    def __init__(self, imgsz: tuple[int, int]) -> None:
        self.imgsz = imgsz
        self.canvas = np.zeros(
            (self.imgsz[1], self.imgsz[0], 3), dtype=np.uint8
        )

        self.tasks: list[Task] = []

    def add_task(
        self,
        name: str,
        task_name: str,
        agent_num: int,
        seed: int,
        fps: int,
        imgsz: tuple[int, int],
        coor_data: CoordinateData,
    ) -> bool:
        task = TaskFactory.get_instance().create_task(task_name)
        task_data = TaskData(agent_num, seed, fps, imgsz, coor_data)

        success = task.init(task_data)

        if not success:
            return False

        task.draw_canvas(self.canvas)

        self.tasks.append(task)

        return True

    def add_task_config(self, name: str, config_path: Path) -> bool:
        config = Config(config_path)
        if not config.load():
            return False

        task_name = config.get_or("taskName", "")
        if not task_name:
            return False

        imgsz_dict: tuple[int, int] = config.get_or(
            "imgsz", {"weight": 0, "height": 0}
        )
        if imgsz_dict["width"] <= 0 or imgsz_dict["height"] <= 0:
            return False
        imgsz = (imgsz_dict["width"], imgsz_dict["height"])

        coor_data = config.get_or("points", {})
        if not coor_data:
            return False

        agent_num = config.get_or("agentNum", 1)
        seed = config.get_or("seed", 123)
        fps = config.get_or("fps", 30)

        return self.add_task(
            name, task_name, agent_num, seed, fps, imgsz, coor_data
        )

    def run(self) -> None:
        while True:
            display_canvas = self.canvas.copy()

            for task in self.tasks:
                detection_list = task.generate()

                self.draw(display_canvas, detection_list)

                task.draw_canvas_status(display_canvas)

            cv2.imshow("Simulation", display_canvas)

            if cv2.waitKey(10) == 27:
                break

        cv2.destroyAllWindows()

    def draw(self, image: np.ndarray, detections: list[Detection]) -> None:
        for detection in detections:
            cv2.circle(
                image,
                np.array([detection.bbox.x, detection.bbox.y], dtype=np.int32),
                5,
                (255, 255, 255),
                -1,
            )

    def write_state(self, image: np.ndarray, summary_str: list[str]) -> None:
        start_x = 15
        start_y = 30
        line_spacing = 25

        for text in summary_str:
            cv2.putText(
                image,
                text,
                (start_x, start_y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )

            start_y += line_spacing

    def get_canvas(self) -> np.ndarray:
        return self.canvas
