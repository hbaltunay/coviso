from dataclasses import dataclass
from pathlib import Path
from typing import Any, Self

import cv2
from numpy.typing import NDArray

from ..loggers import CLogger

logger = CLogger(__name__)


@dataclass
class InfoVideo:
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
            InfoVideo: An object with details about the video.
        """
        cap = cv2.VideoCapture(source_path)
        if not cap.isOpened():
            raise Exception(f"Could not open video at {source_path}")

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        return InfoVideo(width, height, fps, total_frames)


class GetVideo:

    def __init__(
        self, source_path: str, start_time: int = 0, video_time: int = -1
    ) -> None:
        """
        Args:
            source_path (str): The file path of the source file.
            start_time (int): Video start time.
            video_time (int): Video time.
        """
        self.source_path = source_path
        self.cap = cv2.VideoCapture(self.source_path)
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.start_time = int(self.fps * start_time)
        self.video_time = int(self.fps * video_time)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.start_time)
        self.frame_num = 0

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> Any | NDArray[Any]:
        self.frame_num += 1
        ret, video_frame = self.cap.read()
        if ret and self.frame_num != self.video_time:
            return video_frame
        else:
            logger.info("The video is complete.")
            self.cap.release()
            raise StopIteration


class ProcessVideo:
    def __init__(
        self,
        source_path: str | Path,
        target_path: str = "./result.mp4",
        save: bool = False,
        start_time: int = 0,
        video_time: int = -1,
    ) -> None:
        """
        Args:
            source_path (str): The file path of the source file.
            target_path (str): The path where the file will be saved.
            save (bool): Whether the file will be saved.
            start_time (int): Video start time.
            video_time (int): Video time.
        """
        self.source_path = str(source_path)
        self.target_path = target_path
        self.save = save
        self.start_time = start_time
        self.video_time = video_time
        self.out = None
        self.stopped = False

    def __enter__(self) -> Self:
        self.video_info = InfoVideo.get(source_path=self.source_path)
        self.video_frames = GetVideo(
            source_path=self.source_path,
            start_time=self.start_time,
            video_time=self.video_time,
        )
        self.imgsz = (self.video_info.height, self.video_info.width)

        if self.save:
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            self.out = cv2.VideoWriter(
                self.target_path,
                fourcc,
                self.video_info.fps,
                (self.video_info.width, self.video_info.height),
            )

        logger.info("Video processing has started.")

        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        logger.info("Video processing is finished.")
        if self.out:
            self.out.release()
        cv2.destroyAllWindows()

    def show(self, frame: NDArray[Any], winname: str = "Coviso", delay: int = 1):
        cv2.imshow(winname, frame)
        if cv2.waitKey(delay) & 0xFF == ord("q"):
            self.stopped = True
            if self.out:
                self.out.release()
