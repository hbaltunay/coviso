import gradio as gr

from ..loggers import CLogger
from .core import CoreDemo
from .set import SetDemo

logger = CLogger(__name__)


class CovisoAPP:
    def __init__(self) -> None:
        pass

    def create_demo(self):
        with gr.Blocks(title="COVISO") as demo:
            gr.Markdown("# 🚀 **COVISO**")
            SetDemo.render()
        with demo.route("Core"):
            CoreDemo.render()
        return demo

    def run(self):
        demo = self.create_demo()
        demo.launch(server_name="127.0.0.1", server_port=7860, share=False)
