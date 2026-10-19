import math
from dataclasses import dataclass


@dataclass
class MoveData:
    target_coord: list[float] = None
    current_coord: list[float] = None
    current_vel: list[float] = None
    arrived: bool = False
    max_speed: float = 0.0
    max_acceleration: float = 0.0
    current_speed: float = 0.0

    def __post_init__(self) -> None:
        if self.current_vel is None:
            self.current_vel = [0.0, 0.0]
            self.target_coord = [0.0, 0.0]
            self.current_coord = [0.0, 0.0]


class Movement:
    @staticmethod
    def move(move_data: MoveData) -> None:
        to_target_x = move_data.target_coord[0] - move_data.current_coord[0]
        to_target_y = move_data.target_coord[1] - move_data.current_coord[1]

        distance = math.hypot(to_target_x, to_target_y)

        if distance < 0.5:
            move_data.current_coord = list(move_data.target_coord)
            move_data.current_vel = [0.0, 0.0]
            move_data.current_speed = 0.0
            move_data.arrived = True
            return

        direction_x = to_target_x / distance
        direction_y = to_target_y / distance

        braking_distance = (
            move_data.current_speed * move_data.current_speed
        ) / (2.0 * move_data.max_acceleration)

        if distance > braking_distance:
            target_speed = move_data.max_speed
        else:
            target_speed = math.sqrt(
                2.0 * move_data.max_acceleration * distance
            )

        target_vel_x = direction_x * target_speed
        target_vel_y = direction_y * target_speed

        vel_error_x = target_vel_x - move_data.current_vel[0]
        vel_error_y = target_vel_y - move_data.current_vel[1]
        error_len = math.hypot(vel_error_x, vel_error_y)

        if error_len > 0.01:
            accel_dir_x = vel_error_x / error_len
            accel_dir_y = vel_error_y / error_len

            if move_data.max_acceleration > error_len:
                move_data.current_vel = [target_vel_x, target_vel_y]
            else:
                move_data.current_vel[0] += (
                    accel_dir_x * move_data.max_acceleration
                )
                move_data.current_vel[1] += (
                    accel_dir_y * move_data.max_acceleration
                )
        else:
            move_data.current_vel = [target_vel_x, target_vel_y]

        move_data.current_speed = math.hypot(
            move_data.current_vel[0], move_data.current_vel[1]
        )
        move_data.current_coord[0] += move_data.current_vel[0]
        move_data.current_coord[1] += move_data.current_vel[1]
