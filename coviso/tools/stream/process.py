from dataclasses import dataclass
from pathlib import Path
from typing import Any, Self

import cv2
import httpx
import numpy as np
from numpy.typing import NDArray

from ...loggers import CLogger

logger = CLogger(__name__)

URL_STREAM = "http://localhost:8000/stream/"
URL_PREDICT = "http://localhost:8001/predict/"
URL_SETUP = "http://localhost:8001/setup/"


@dataclass
class InfoStream:
    width: int
    height: int
    fps: int
    total_frames: int | None = None

    @classmethod
    def get(cls, source_path: str):
        """
        Args:
            source_path (str): The file path of the source file.
        Returns:
            InfoStream: An object with details about the stream.
        """
        cap = cv2.VideoCapture(source_path)
        if not cap.isOpened():
            raise Exception(f"Could not open video at {source_path}")

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        return InfoStream(width, height, fps, total_frames)


class GetStream:
    def __init__(self, source_path: str, total_time: int = -1) -> None:
        self.source_path = source_path
        self.total_time = total_time

    def __iter__(self):
        self.client = httpx.Client()
        self.client_stream = self.client.stream(
            "POST", URL_STREAM, params={"source_path": self.source_path}
        )
        self.response = self.client_stream.__enter__()
        if self.response.status_code != 200:
            raise RuntimeError(f"Connection failed: {self.response.status_code}")
        self.buffer = b""
        self.bytes_iter = self.response.iter_bytes()
        return self

    def __next__(self) -> Any:
        chunk = next(self.bytes_iter)
        self.buffer += chunk

        start = self.buffer.find(b"\xff\xd8")
        end = self.buffer.find(b"\xff\xd9")

        if start != -1 and end != -1:
            jpg_data = self.buffer[start : end + 2]
            self.buffer = self.buffer[end + 2 :]

            img_array = np.frombuffer(jpg_data, dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            if frame is not None:
                return frame

        return self.__next__()

    def close(self):
        self.response.__exit__(None, None, None)
        self.client.close()


class ProcessStream:
    def __init__(
        self,
        source_path: str | Path,
        target_path: str = "./result.mp4",
        save: bool = False,
        video_time: int = -1,
    ) -> None:
        self.source_path = str(source_path)
        self.target_path = target_path
        self.save = save
        self.video_time = video_time
        self.out = None
        self.stopped = False

    def stop(self):
        if self.client:
            self.client.aclose()

    def setup(self, source_path: str) -> Any:

        response = self.client.post(
            URL_SETUP,
            data={"source_path": source_path},
        )

        return response.json()

    def send_image(self, frame: Any, frame_num: int) -> Any:
        _, buffer = cv2.imencode(".jpg", frame)
        response = self.client.post(
            URL_PREDICT,
            files={"file": ("frame.jpg", buffer.tobytes(), "image/jpeg")},
            data={"frame_num": frame_num, "source_path": "A"},
        )

        return response.json()

    def __enter__(self) -> Self:
        self.client = httpx.Client()
        _ = self.setup(source_path=self.source_path)
        self.stream_info = InfoStream.get(source_path=self.source_path)
        self.stream = GetStream(
            source_path=self.source_path, total_time=self.video_time
        )
        self.imgsz = (self.stream_info.height, self.stream_info.width)

        if self.save:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            self.out = cv2.VideoWriter(
                self.target_path,
                fourcc,
                self.stream.fps,
                (self.stream.width, self.stream.height),
            )

        logger.info("Stream processing has started.")

        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        logger.info("Stream processing is finished.")
        if self.out:
            self.out.release()
        cv2.destroyAllWindows()

    def show(
        self, frame: NDArray[Any], winname: str = "Coviso", delay: int = 1
    ) -> None:
        cv2.imshow(winname, frame)
        if cv2.waitKey(delay) & 0xFF == ord("q"):
            self.stopped = True
            if self.out:
                self.out.release()
