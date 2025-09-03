import threading
from queue import Queue
from typing import Any

import cv2
import uvicorn
from fastapi import APIRouter, FastAPI, Query, Response
from fastapi.responses import StreamingResponse

from ...loggers import CLogger

logger = CLogger(__name__)

app = FastAPI()

router = APIRouter()


class APIStream:
    def __init__(self, source_path: str, queue_size: int = 2) -> None:
        self.source_path = source_path
        self.queue_size = queue_size
        self.stopped = False
        self.completed = False
        self.first_frame_event = threading.Event()

    def start(self) -> None:
        self.cap = cv2.VideoCapture(self.source_path)
        self.queue = Queue(maxsize=self.queue_size)
        self.thread = threading.Thread(target=self.update, daemon=True)
        self.thread.start()
        if not self.first_frame_event.wait(timeout=3):
            logger.error("First frame not received within timeout")

    def update(self) -> None:
        while not self.stopped:
            ret, frame = self.cap.read()

            if not ret:
                self.stop()
                break
            self.queue.put(frame, timeout=3)

            if not self.first_frame_event.is_set():
                self.first_frame_event.set()

    def read(self) -> Any:
        return self.queue.get(timeout=3)

    def stop(self) -> None:
        self.stopped = True
        self.cap.release()


class StreamManager:
    def __init__(self) -> None:
        self.streams: dict[str, APIStream] = {}

    def get_streamer(self, source_path: str) -> APIStream:
        if not source_path in self.streams or self.streams[source_path].completed:
            self.streams[source_path] = APIStream(source_path=source_path)

        return self.streams[source_path]


STREAMS = StreamManager()


async def stream_generator(stream: APIStream):
    while not stream.stopped:
        frame = stream.read()

        _, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()
        yield (
            b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )
    stream.completed = True


@app.post("/stream/")
async def get_stream(source_path: str = Query()) -> Response:
    stream = STREAMS.get_streamer(source_path)
    stream.start()

    return StreamingResponse(
        stream_generator(stream=stream),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("core:app", host="127.0.0.1", port=8000, reload=True)
