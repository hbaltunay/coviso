import tempfile
import uuid
from pathlib import Path

import cv2
import gradio as gr
import numpy as np

from ..loggers import CLogger
from ..solutions import LineTracker, Tracker, ZoneTracker
from ..tools import ProcessStream
from ..utils.file import CFGManager

logger = CLogger(__name__)


VIDEOS_PATH = Path.home() / "Coviso/data/videos"
CONFIG_PATH = Path.home() / "Coviso/cfg"


SOLUTIONS = {
    "Zone Tracker": [ZoneTracker, "zone-config.json"],
    "Line Tracker": [LineTracker, "line-config.json"],
}

GRADIO_TEMP_PATH = Path(tempfile.gettempdir()) / "gradio"


class CoreAPP:
    def __init__(self) -> None:
        pass

    def create_processor(self, solution: str) -> tuple[Tracker, str] | None:

        processor, config_name = SOLUTIONS.get(solution, [None, None])

        if processor is None:
            raise ValueError("Not found solution!")
        else:
            return processor, config_name

    def frame_process(self, solution: str):
        processor, config_name = self.create_processor(solution)  # type: ignore
        self.config_path = str(CONFIG_PATH / config_name)
        self.config = CFGManager(self.config_path)
        self.processor = processor(self.config.cfg_dict)
        self.processor.setup(self.config.cfg_dict)

        source_path = self.config.cfg_dict["source_path"]

        with ProcessStream(source_path=source_path) as ps:
            self.processor.create_mask(size=ps.imgsz)

            video_codec = cv2.VideoWriter_fourcc(*"mp4v")  # type: ignore
            fps = ps.stream_info.fps
            width = ps.stream_info.width // 2
            height = ps.stream_info.height // 2
            batch = []
            for i, frame in enumerate(ps.stream):

                response = ps.send_image(frame=frame, frame_num=i)

                result = np.array(response["result"])

                frame, _ = self.processor.process(frame=frame, result=result)

                frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

                batch.append(frame)

                if i % 60 == 0:

                    output_video_name = f"output_{uuid.uuid4()}.mp4"
                    output_video_path = str(GRADIO_TEMP_PATH / output_video_name)
                    output_video = cv2.VideoWriter(
                        output_video_path, video_codec, fps, (width, height)
                    )
                    for fr in batch:
                        output_video.write(fr)
                    output_video.release()

                    batch = []

                    yield output_video_path

    def create_demo(self):
        with gr.Blocks() as demo:
            with gr.Column():
                solutions_ddown = gr.Dropdown(
                    choices=["Zone Tracker", "Line Tracker"],
                    label="Solutions",
                    interactive=True,
                )
                start_btn = gr.Button("Start")

            frame = gr.Video("Frame", streaming=True, autoplay=True)

            start_btn.click(
                self.frame_process, inputs=[solutions_ddown], outputs=[frame]
            )

        return demo

    def render(self):
        self.demo.render()

    def run(self):
        self.demo = self.create_demo()

        # self.demo.launch(server_name="127.0.0.1", server_port=7860, share=False)


CoreDemo = CoreAPP()
CoreDemo.run()
