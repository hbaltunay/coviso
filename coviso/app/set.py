import time
from collections import deque
from pathlib import Path
from typing import Any

import cv2
import gradio as gr
import numpy as np

from ..loggers import CLogger
from ..utils.file import CFGManager

logger = CLogger(__name__)


VIDEOS_PATH = Path.home() / "Coviso/data/videos"
CONFİG_PATH = Path.home() / "Coviso/cfg"


class SetAPP:
    def __init__(self) -> None:
        self.points: deque[list[int]] = deque()
        self.video_path = ""
        self.config_name = None
        self.polys = {}
        self.last_num = 0
        self.editable = False
        self.enable_upload = True
        self.active = True

    def select_solution(self, solution: str):
        if solution == "Zone Tracker":
            self.config_name = "zone-config.json"
            return gr.update(value=0, interactive=True)
        elif solution == "Line Tracker":
            self.config_name = "line-config.json"
            return gr.update(value=3, interactive=False)

    def read_video_first_frame(self, video_path: str):
        self.video_path = str(VIDEOS_PATH / video_path)
        cap = cv2.VideoCapture(self.video_path)
        _, frame = cap.read()
        cap.release()

        self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.processed_frame = self.frame.copy()

    def frame_process(self, video_path: str, solution: str, point_num: str):
        self.solution = solution
        self.point_num = int(point_num)
        self.read_video_first_frame(video_path)
        if self.solution == "Zone Tracker" and self.point_num < 3:
            self.point_num = 4

        self.points = deque(maxlen=self.point_num)

        if self.config_name is None:
            _ = self.select_solution(self.solution)

        self.config_path = str(CONFİG_PATH / self.config_name)  # type: ignore
        self.config = CFGManager(self.config_path)

        self.update()

        info_text = f"Solution: {self.solution} - Point Num: {self.point_num}"

        self.draw_polys()

        return (
            self.processed_frame,
            gr.update(value=self.point_num),
            info_text,
            gr.update(visible=True),
            gr.update(interactive=True),
            gr.update(visible=False),
        )

    def clear_output(self):
        self.config_name = None
        self.points = deque()
        self.last_num = 0
        self.active = False
        time.sleep(1)
        return (
            None,
            gr.update(visible=False),
            gr.update(interactive=False),
            gr.update(visible=False),
        )

    def undo_click(self):
        if self.points:
            self.points.pop()
            self.draw_polys()

    def add_click(self):
        if len(self.points) == self.point_num:
            self.last_num += 1
            self.polys[f"poly_{self.last_num}"] = list(self.points)
            self.points = deque(maxlen=self.point_num)

    def del_click(self):
        if self.polys:
            self.polys.pop(f"poly_{self.last_num}")
            self.last_num -= 1
            self.points = deque(maxlen=self.point_num)
            self.draw_polys()

    def save_click(self):
        last_dict = {
            "source_path": self.video_path,
            "solution": self.solution,
            "polys": self.polys,
        }
        self.config.write_file(last_dict)

    def draw_polys(self) -> Any:
        self.enable_upload = True
        self.processed_frame = self.frame.copy()

        poly = [*self.polys.values()]
        poly.append(self.points)  # type: ignore

        is_closed = self.solution == "Zone Tracker"
        for pl in poly:
            cv2.polylines(
                self.processed_frame,
                [np.array(pl, dtype=np.int32)],
                isClosed=is_closed,
                color=(255, 0, 0),
                thickness=2,
            )
            for x, y in pl:
                cv2.circle(
                    self.processed_frame,
                    (x, y),
                    radius=2,
                    color=(0, 255, 0),
                    thickness=-1,
                )

    def image_select(self, event: gr.EventData) -> Any:
        if self.editable:
            x, y = event._data["index"]  # type: ignore

            self.points.append([int(x), int(y)])
            self.draw_polys()

    def upload_image(self):
        self.active = True
        self.editable = True

        while self.active:
            if self.enable_upload:
                yield self.processed_frame
                self.enable_upload = False
            time.sleep(0.5)

    def create_demo(self):
        with gr.Blocks() as demo:

            with gr.Column():
                video_path = gr.Textbox(value="2.mp4", label="Video Path")

            with gr.Row():
                solutions_ddown = gr.Dropdown(
                    choices=["Zone Tracker", "Line Tracker"],
                    label="Solutions",
                    interactive=True,
                )
                point_tbox = gr.Textbox(value="0", label="Point Number")

            with gr.Row():
                show_btn = gr.Button("Show")
                reset_btn = gr.Button("Reset")

            info_text = gr.Button(visible=False)
            first_frame = gr.Image(label="Video First Frame", streaming=True)

            edit_btn = gr.Button("Edit", interactive=False)

            with gr.Row(visible=False) as edit_row:
                undo_btn = gr.Button("Undo")
                add_btn = gr.Button("Add")
                del_btn = gr.Button("Delete")
                save_btn = gr.Button("Save")

            solutions_ddown.change(
                self.select_solution,
                inputs=[solutions_ddown],
                outputs=[point_tbox],
            )

            show_btn.click(
                fn=self.frame_process,
                inputs=[video_path, solutions_ddown, point_tbox],
                outputs=[
                    first_frame,
                    point_tbox,
                    info_text,
                    info_text,
                    edit_btn,
                    edit_row,
                ],
            )

            reset_btn.click(
                fn=self.clear_output,
                inputs=None,
                outputs=[first_frame, info_text, edit_btn, edit_row],
            )

            edit_btn.click(fn=self.upload_image, inputs=None, outputs=[first_frame])
            edit_btn.click(
                fn=lambda: gr.update(visible=True), inputs=None, outputs=[edit_row]
            )

            first_frame.select(self.image_select)

            undo_btn.click(self.undo_click)
            add_btn.click(self.add_click)
            del_btn.click(self.del_click)
            save_btn.click(self.save_click)

        return demo

    def update(self):
        self.polys = {}
        self.active = False
        self.editable = False
        self.enable_upload = True
        polys = self.config.cfg_dict.get("polys", None)

        if polys is not None:
            self.polys.update(polys)
            self.last_num = len(polys)

    def render(self):
        self.demo.render()

    def run(self):
        self.demo = self.create_demo()

        # demo.launch(server_name="127.0.0.1", server_port=7860, share=False)


SetDemo = SetAPP()
SetDemo.run()
