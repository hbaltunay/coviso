import numpy as np

from coviso.solution.state import LineState, ZoneState


def draw_zone(image: np.ndarray, state: ZoneState) -> None:
    state.draw(image)


def draw_line(image: np.ndarray, state: LineState) -> None:
    state.draw(image)
