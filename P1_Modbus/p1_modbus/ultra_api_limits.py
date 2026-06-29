"""Physical parameter limits for UltraArmP1Modbus (docs/ultraArm_P1_zh.md)."""

from __future__ import annotations

from collections.abc import Callable, Sequence

# 来源：docs/ultraArm_P1_zh.md §set_angle / §set_coords
JOINT_ANGLE_LIMITS: dict[int, tuple[float, float]] = {
    1: (-165.0, 165.0),
    2: (-18.0, 85.0),
    3: (89.0, 200.0),
    4: (-179.0, 179.0),
}

COORD_AXIS_LIMITS: dict[int, tuple[float, float]] = {
    1: (-301.7, 360.5),  # X
    2: (-360.5, 360.5),  # Y
    3: (-157.0, 91.0),  # Z
    4: (-180.0, 180.0),  # RX
}

SPEED_RANGE: tuple[int, int] = (1, 100)
RGB_RANGE: tuple[int, int] = (0, 255)
PWM_LEVEL_RANGE: tuple[int, int] = (0, 255)
PWM_MODE_RANGE: tuple[int, int] = (0, 1)
PUMP_STATE_RANGE: tuple[int, int] = (0, 2)
GRIPPER_ANGLE_RANGE: tuple[int, int] = (1, 100)
GRIPPER_PARAM_ADDR_RANGE: tuple[int, int] = (1, 69)
GRIPPER_PARAM_VALUE_RANGE: tuple[int, int] = (0, 65535)
BASE_IO_PIN_RANGE: tuple[int, int] = (1, 10)
END_IO_PIN_RANGE: tuple[int, int] = (1, 4)
DIGITAL_IO_OUTPUT_PIN_RANGE: tuple[int, int] = (3, 4)
IO_MODE_RANGE: tuple[int, int] = (0, 1)
IO_SIGNAL_RANGE: tuple[int, int] = (0, 1)
JOINT_ID_RANGE: tuple[int, int] = (0, 4)
ZERO_CALIB_CLEAR_RANGE: tuple[int, int] = (1, 4)
CONVEYOR_STATE_RANGE: tuple[int, int] = (0, 1)
CONVEYOR_DIRECTION_RANGE: tuple[int, int] = (0, 1)
CONVEYOR_SPEED_RANGE: tuple[int, int] = (50, 500000)
CONVEYOR_DISTANCE_RANGE: tuple[int, int] = (0, 1200)
JOG_DIRECTION_RANGE: tuple[int, int] = (0, 1)


def validate_if(enabled: bool, fn: Callable[..., None], /, *args, **kwargs) -> None:
    """enabled 为 False 时跳过 fn（供 UltraArmP1Modbus.validate_limits 使用）。"""
    if enabled:
        fn(*args, **kwargs)


def _in_range(name: str, value: float | int, lo: float, hi: float) -> None:
    v = float(value)
    if v < lo or v > hi:
        raise ValueError(f"{name} 超出范围 [{lo}, {hi}]，当前值 {value!r}")


def validate_joint_id(joint_id: int, *, allow_all: bool = True) -> None:
    lo = JOINT_ID_RANGE[0] if allow_all else 1
    _in_range("joint_id", joint_id, lo, JOINT_ID_RANGE[1])


def validate_axis_id(axis_id: int) -> None:
    _in_range("axis_id", axis_id, 1, 4)


def validate_joint_angle(joint_id: int, angle: float | int) -> None:
    validate_joint_id(joint_id, allow_all=False)
    lo, hi = JOINT_ANGLE_LIMITS[joint_id]
    _in_range(f"J{joint_id} 角度", angle, lo, hi)


def validate_joint_angles(angles: Sequence[float | int]) -> None:
    if len(angles) != 4:
        raise ValueError("angles 长度须为 4")
    for i, a in enumerate(angles, start=1):
        validate_joint_angle(i, a)


def validate_coord_axis(axis_id: int, value: float | int) -> None:
    validate_axis_id(axis_id)
    lo, hi = COORD_AXIS_LIMITS[axis_id]
    _in_range(f"轴{axis_id} 坐标", value, lo, hi)


def validate_coords(coords: Sequence[float | int]) -> None:
    if len(coords) not in (3, 4):
        raise ValueError("coords 长度须为 3 或 4")
    for i, c in enumerate(coords[:4], start=1):
        if i <= len(coords):
            validate_coord_axis(i, c)


def validate_speed(speed: float | int) -> None:
    _in_range("speed", speed, SPEED_RANGE[0], SPEED_RANGE[1])


def validate_rgb(r: int, g: int, b: int) -> None:
    _in_range("r", r, *RGB_RANGE)
    _in_range("g", g, *RGB_RANGE)
    _in_range("b", b, *RGB_RANGE)


def validate_pwm_level(level: int) -> None:
    _in_range("pwm_level", level, *PWM_LEVEL_RANGE)


def validate_pwm_mode(state: int | bool) -> None:
    _in_range("pwm_mode", int(state), *PWM_MODE_RANGE)


def validate_pump_state(state: int) -> None:
    _in_range("pump_state", state, *PUMP_STATE_RANGE)


def validate_gripper_angle(angle: int) -> None:
    _in_range("gripper_angle", angle, *GRIPPER_ANGLE_RANGE)


def validate_gripper_speed(speed: int) -> None:
    _in_range("gripper_speed", speed, *GRIPPER_ANGLE_RANGE)


def validate_gripper_addr(addr: int) -> None:
    _in_range("addr", addr, *GRIPPER_PARAM_ADDR_RANGE)


def validate_gripper_param_value(value: int) -> None:
    _in_range("parameter_value", value, *GRIPPER_PARAM_VALUE_RANGE)


def validate_base_io_pin(pin_no: int) -> None:
    _in_range("pin_no", pin_no, *BASE_IO_PIN_RANGE)


def validate_end_io_pin(pin_no: int) -> None:
    _in_range("pin_no", pin_no, *END_IO_PIN_RANGE)


def validate_digital_output_pin(pin_no: int) -> None:
    _in_range("pin_no", pin_no, *DIGITAL_IO_OUTPUT_PIN_RANGE)


def validate_io_mode(mode: int) -> None:
    _in_range("pin_status", mode, *IO_MODE_RANGE)


def validate_io_signal(signal: int) -> None:
    _in_range("pin_signal", signal, *IO_SIGNAL_RANGE)


def validate_conveyor(state: int, direction: int, speed: int, distance: int) -> None:
    _in_range("state", state, *CONVEYOR_STATE_RANGE)
    _in_range("direction", direction, *CONVEYOR_DIRECTION_RANGE)
    _in_range("speed", speed, *CONVEYOR_SPEED_RANGE)
    _in_range("distance", distance, *CONVEYOR_DISTANCE_RANGE)


def validate_jog_direction(direction: int | bool) -> None:
    d = 1 if direction is True else 0 if direction is False else int(direction)
    _in_range("direction", d, *JOG_DIRECTION_RANGE)
