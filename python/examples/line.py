from typing import Any

import cv2
from coviso.sim import Simulator
from coviso.solution import LineTracker


def on_mouse(event: int, x: int, y: int, flags: int, param: Any) -> None:  # noqa
    sim: Simulator = param

    if event == cv2.EVENT_LBUTTONDOWN:
        for task in sim.tasks:
            for _, agent_data in task.get_agent_map().items():
                agent_data.move_data.target_coord = (x, y)


def main() -> None:
    sim = Simulator((1280, 720))

    config_path = "config/line_config.json"

    sim.add_task_config("Test", config_path)

    tracker = LineTracker(config_path)
    tracker.init()

    window_name = "Simulator"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window_name, on_mouse, sim)
    cv2.resizeWindow(window_name, 800, 600)

    im = cv2.imread("canvas.jpg")
    canvas = cv2.resize(im, (1280, 720))

    while True:
        display_canvas = canvas.copy()

        for task in sim.tasks:
            detection_list = task.generate()
            tracker.process(display_canvas, detection_list)

            sim.draw(display_canvas, detection_list)
            infos = tracker.get_state_info_str()
            sim.write_state(display_canvas, infos)

        cv2.imshow(window_name, display_canvas)

        if cv2.waitKey(33) == 27:
            break


if __name__ == "__main__":
    main()
