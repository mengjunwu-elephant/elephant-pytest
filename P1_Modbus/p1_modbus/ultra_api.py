"""
UltraArm P1 high-level API: ``get_*`` / ``set_*`` naming aligned with ``ultraArm P1协议文档.xlsx``
and common host SDK conventions.

- **get_*** return ``int``, ``list[int]``, or ``list[float]`` (e.g. M405 angles in degrees).
- **set_*** return ``int`` ``0`` on successful transaction (raises on timeout / protocol error).

Low-level G/M helpers remain on :class:`P1Client` unchanged.
"""

from __future__ import annotations

import logging
import struct
from collections.abc import Callable, Sequence
from typing import cast

from p1_modbus.commands import P1Client
from p1_modbus.models import ConveyorParams, GripperParams, PreviewPose, RgbColor


def _u8_list(data: bytes) -> list[int]:
    return [int(b) for b in data]


def _be_i16_list(data: bytes) -> list[int]:
    if len(data) % 2 != 0:
        return _u8_list(data)
    fmt = ">" + "h" * (len(data) // 2)
    return list(struct.unpack(fmt, data))


def _bytes_u8(seq: Sequence[int], expected_len: int, *, label: str) -> bytes:
    if len(seq) != expected_len:
        raise ValueError(f"{label}: need {expected_len} bytes, got {len(seq)}")
    return bytes(int(x) & 0xFF for x in seq)


def _to_centimil(x: float | int) -> int:
    """Physical degrees or millimetres → centi-units (×100) for int16 wire format."""
    v = int(round(float(x) * 100.0))
    if v < -32768 or v > 32767:
        raise ValueError(f"value out of int16 range after ×100: {x!r} -> {v}")
    return v


def _pack_4_axes_speed_10(axes: Sequence[float | int], speed: float | int) -> bytes:
    """G0/G1 10-byte payload: 4× int16 BE (axes) + int16 BE (speed), all centi-units (×100)."""
    if len(axes) != 4:
        raise ValueError("axes must have exactly 4 entries (degrees or mm each); speed is separate")
    return struct.pack(
        ">hhhhh",
        _to_centimil(axes[0]),
        _to_centimil(axes[1]),
        _to_centimil(axes[2]),
        _to_centimil(axes[3]),
        _to_centimil(speed),
    )


def _pack_2_axes_speed_6(axes: Sequence[float | int], speed: float | int) -> bytes:
    """6-byte payload: 2× int16 BE (axes) + int16 BE (speed), all centi-units (×100)."""
    if len(axes) != 2:
        raise ValueError("axes must have exactly 2 entries (degrees or mm each); speed is separate")
    return struct.pack(">hhh", _to_centimil(axes[0]), _to_centimil(axes[1]), _to_centimil(speed))


def _is_coord_sequence(obj: object) -> bool:
    """True for list/tuple of numbers; False for str/bytes/scalar."""
    return isinstance(obj, Sequence) and not isinstance(obj, (str, bytes))


def _pack_axis_value_speed_6(axis_1based: int, value: float | int, speed: float | int) -> bytes:
    """
    G1 单关节 / 单坐标 6 字节：``轴号(1–4)``、``目标(×100 大端 int16)``、``速度(×100)``。

    例：关节 1 → 0°、速度 100 → ``00 01 00 00 27 10``。
    """
    a = int(axis_1based)
    if a < 1 or a > 4:
        raise ValueError("axis must be 1..4 (关节 1–4 或坐标 X,Y,Z,RX)")
    return struct.pack(">hhh", a, _to_centimil(value), _to_centimil(speed))


def _direction_to_i16(d: int | bool) -> int:
    """M13/M14 方向字段：1 正向，0 反向（大端 int16）。"""
    if isinstance(d, bool):
        return 1 if d else 0
    di = int(d)
    if di not in (0, 1):
        raise ValueError("direction must be 0 (reverse), 1 (forward), or bool")
    return di


def _pack_jog_axis_direction_speed_6(axis_1based: int, direction: int | bool, speed: float | int) -> bytes:
    """M13/M14：轴号 1–4（关节 A–D 或坐标维）+ 方向 0/1 + 速度（×100，同 set_angle）。"""
    a = int(axis_1based)
    if a < 1 or a > 4:
        raise ValueError("axis must be 1..4 (关节 A–D 或坐标 X,Y,Z,RX)")
    return struct.pack(">hhh", a, _direction_to_i16(direction), _to_centimil(speed))


def _pack_jog_axis_step_speed_6(axis_1based: int, step: float | int, speed: float | int) -> bytes:
    """M19/M20：轴号 1–4 + 步进量（度/mm ×100）+ 速度（×100）。"""
    a = int(axis_1based)
    if a < 1 or a > 4:
        raise ValueError("axis must be 1..4 (关节 A–D 或坐标 X,Y,Z,RX)")
    return struct.pack(">hhh", a, _to_centimil(step), _to_centimil(speed))


def _write_ok(_: bytes) -> int:
    return 0


class UltraArmP1Modbus(P1Client):
    """
    UltraArm P1 Modbus RTU facade with ``get_*`` / ``set_*``.

    With ``debug=True``, the base client attaches a stderr logging handler so **TX/RX**
    frames are printed without extra :mod:`logging` setup.

    The serial port opens automatically on the first command (no need to call :meth:`~p1_modbus.client.P1ClientBase.open`).
    """

    def __init__(
        self,
        port: str,
        baudrate: int = 115200,
        timeout: float = 0.3,
        debug: bool = False,
        *,
        write_timeout: float | None = None,
        event_hook: Callable[[bytes], None] | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        super().__init__(
            port,
            baudrate,
            timeout,
            debug,
            write_timeout=write_timeout,
            event_hook=event_hook,
            logger=logger,
        )

    # --- firmware (G6/G7, M401/M402) ---
    def get_system_version(self) -> int:
        """G6: main MCU firmware version (u16 BE, e.g. ``00 0A`` → 10)."""
        return int(self.read_main_fw_version())

    def get_modify_version(self) -> int:
        """G7: main MCU correction / patch byte."""
        return int(self.read_main_fw_patch())

    def get_system_screen_version(self) -> int:
        """M401: screen firmware version (u16 BE, e.g. ``00 0C`` → 12)."""
        return int(self.read_display_fw_version())

    def get_screen_modify_version(self) -> int:
        """M402: screen correction / patch byte."""
        return int(self.read_display_fw_patch())

    # --- pose / state reads (M405/M406/G8/M200/M600) ---
    def get_angles(self) -> list[float]:
        """
        M405: joint angles in **degrees** (device sends big-endian signed int16 **centidegrees**, ÷100).

        Example raw ``DD 36`` → -8906 → **-89.06**°.
        """
        raw = _be_i16_list(self.m405_read_angles())
        return [x / 100.0 for x in raw]

    def get_coords(self) -> list[float]:
        """
        M406: coordinates in **same unit as device int16 centi-units** (typically mm×100), ÷100.

        Same packing as angles: big-endian signed int16 per value.
        """
        raw = _be_i16_list(self.m406_read_coordinates())
        return [x / 100.0 for x in raw]

    def get_errors(self) -> list[int]:
        """G8: error dword as list of u8 (MSB..LSB order of payload bytes)."""
        return _u8_list(self.g8_read_errors())

    def get_runtime_state(self) -> int:
        """M200: main runtime state byte."""
        return int(self.m200_read_main_runtime_state())

    def get_buffer_size(self) -> int:
        """M600: motion buffer size (u16 BE)."""
        return int(self.m600_read_motion_buffer_size())

    def get_motor_status(self) -> list[int]:
        """M22: five motor status bytes."""
        return list(self.m22_read_motor_status())

    def get_zero_calibration_state(self) -> list[int]:
        """M119: four joints zero-calibration flags."""
        return list(self.m119_read_zero_calibration_state())

    def get_gripper_angle_centideg(self) -> int:
        """M50: gripper angle raw u16 (divide by 100 for degrees per protocol note)."""
        return int(self.m50_read_gripper_angle_centideg())

    def get_gripper_motion_state(self) -> int:
        """M27: gripper motion state u16 BE."""
        return int(self.m27_read_gripper_motion_state())

    def get_gripper_param(self, j: int, k: int) -> int:
        """M26: read gripper parameter slot selected by J/K (L unused, sent as 0)."""
        return int(self.m26_read_gripper_params(GripperParams(j & 0xFFFF, k & 0xFFFF, 0)))

    def get_base_io(self) -> list[int]:
        """M61: base IO raw bytes."""
        return _u8_list(self.m61_read_base_io())

    def get_tool_io(self) -> list[int]:
        """M63: tool/end IO raw bytes."""
        return _u8_list(self.m63_read_tool_io())

    def get_pose_preview_ok(self, pose8: Sequence[int]) -> int:
        """
        M51: preview reachability. Returns ``1`` if device reports reachable (``00 01``), else ``0``.
        ``pose8`` must be eight byte values (0..255).
        """
        payload = _bytes_u8(pose8, 8, label="pose8")
        ok = self.m51_preview(PreviewPose(payload))
        return 1 if ok else 0

    # --- motion / machine writes ---
    def set_coords(
        self,
        x_or_axes: Sequence[float | int] | float | int,
        y_or_speed: float | int | None = None,
        z: float | int | None = None,
        rx: float | int | None = None,
        speed: float | int | None = None,
        *,
        max_speed: bool = True,
    ) -> int:
        """
        坐标运动（4 维 + speed，10 字节）。轴 **1=X, 2=Y, 3=Z, 4=RX**。

        - 推荐：``set_coords(x, y, z, rx, speed, *, max_speed=True)``
        - 兼容：``set_coords([x, y, z, rx], speed, *, max_speed=...)``
        - ``max_speed=True``（默认）：G0 最大速度；``False``：G1 规定速度坐标。
        """
        if _is_coord_sequence(x_or_axes):
            if speed is not None:
                raise ValueError("set_coords([x,y,z,rx], speed): do not pass keyword speed= when using list form")
            if y_or_speed is None:
                raise ValueError("set_coords(axes, speed): need speed as second argument")
            axes = cast(Sequence[float | int], x_or_axes)
            if len(axes) != 4:
                raise ValueError("axes must have exactly 4 entries (X,Y,Z,RX)")
            payload = _pack_4_axes_speed_10(axes, y_or_speed)
        else:
            if y_or_speed is None or z is None or rx is None or speed is None:
                raise ValueError(
                    "set_coords(x, y, z, rx, speed): need five numbers "
                    "(axis 1–4 = X,Y,Z,RX then speed); or set_coords([x,y,z,rx], speed)"
                )
            payload = _pack_4_axes_speed_10(
                (x_or_axes, y_or_speed, z, rx),
                speed,
            )
        if max_speed:
            return _write_ok(self.g0_coordinate_max_speed(payload))
        return _write_ok(self.g1_coordinate_fixed_speed(payload))

    def set_coord(
        self,
        axis_or_axes: int | Sequence[float | int],
        value_or_speed: float | int,
        speed: float | int | None = None,
    ) -> int:
        """
        G1 单坐标（6 字节）。

        - ``set_coord(axis, value, speed)``：``axis`` 为 **1–4**（X,Y,Z,RX）；线格式为
          ``轴号 int16 + 目标×100 + 速度×100``（与单关节相同排布）。
        - ``set_coord([axis, value], speed)``：首元须为 ``int`` 且 1–4，与三参数等价。
        - 首元为浮点等时：仍按 **两坐标分量 + 速度** 的旧 6 字节。
        """
        if speed is None:
            axes = cast(Sequence[float | int], axis_or_axes)
            if len(axes) != 2:
                raise ValueError("set_coord: need two values in sequence, or use set_coord(axis, value, speed)")
            if isinstance(axes[0], int) and 1 <= axes[0] <= 4:
                return _write_ok(
                    self.g1_single_coordinate(_pack_axis_value_speed_6(axes[0], float(axes[1]), value_or_speed))
                )
            return _write_ok(self.g1_single_coordinate(_pack_2_axes_speed_6(axes, value_or_speed)))
        if not isinstance(axis_or_axes, int):
            raise TypeError("set_coord(axis, value, speed): axis must be int 1..4 when three arguments are used")
        return _write_ok(
            self.g1_single_coordinate(_pack_axis_value_speed_6(axis_or_axes, float(value_or_speed), speed))
        )

    def set_angles(
        self,
        j1_or_axes: Sequence[float | int] | float | int,
        j2_or_speed: float | int | None = None,
        j3: float | int | None = None,
        j4: float | int | None = None,
        speed: float | int | None = None,
    ) -> int:
        """
        G1 关节（4 关节 + speed，10 字节）。轴 **1–4** 对应四个关节角顺序。

        - 推荐：``set_angles(j1, j2, j3, j4, speed)``
        - 兼容：``set_angles([j1,j2,j3,j4], speed)``
        """
        if _is_coord_sequence(j1_or_axes):
            if speed is not None:
                raise ValueError("set_angles([...], speed): do not pass keyword speed= when using list form")
            if j2_or_speed is None:
                raise ValueError("set_angles(axes, speed): need speed as second argument")
            axes = cast(Sequence[float | int], j1_or_axes)
            if len(axes) != 4:
                raise ValueError("axes must have exactly 4 entries")
            payload = _pack_4_axes_speed_10(axes, j2_or_speed)
        else:
            if j2_or_speed is None or j3 is None or j4 is None or speed is None:
                raise ValueError(
                    "set_angles(j1, j2, j3, j4, speed): need five numbers "
                    "or set_angles([j1,j2,j3,j4], speed)"
                )
            payload = _pack_4_axes_speed_10((j1_or_axes, j2_or_speed, j3, j4), speed)
        return _write_ok(self.g1_joint(payload))

    def set_angle(
        self,
        axis_or_axes: int | Sequence[float | int],
        value_or_speed: float | int,
        speed: float | int | None = None,
    ) -> int:
        """
        G1 单关节（6 字节）。

        - ``set_angle(axis, value, speed)``：``axis`` 为 **1–4**；线格式为
          ``关节号 int16 + 角度×100 + 速度×100``（例：关节 1、0°、速度 100 → ``00 01 00 00 27 10``）。
        - ``set_angle([axis, value], speed)``：首元须为 ``int`` 且 1–4，与三参数等价。
        - 首元为浮点等时：仍按 **两关节角 + 速度** 的旧 6 字节（两 int16 + speed）。
        """
        if speed is None:
            axes = cast(Sequence[float | int], axis_or_axes)
            if len(axes) != 2:
                raise ValueError("set_angle: need two values in sequence, or use set_angle(axis, value, speed)")
            if isinstance(axes[0], int) and 1 <= axes[0] <= 4:
                return _write_ok(
                    self.g1_single_joint(_pack_axis_value_speed_6(axes[0], float(axes[1]), value_or_speed))
                )
            return _write_ok(self.g1_single_joint(_pack_2_axes_speed_6(axes, value_or_speed)))
        if not isinstance(axis_or_axes, int):
            raise TypeError("set_angle(axis, value, speed): axis must be int 1..4 when three arguments are used")
        return _write_ok(self.g1_single_joint(_pack_axis_value_speed_6(axis_or_axes, float(value_or_speed), speed)))

    def set_reboot_stm32(self) -> int:
        """G10."""
        return _write_ok(self.g10_reboot_stm32())

    def set_unlock(self) -> int:
        """M5."""
        return _write_ok(self.m5_unlock())

    def set_jog_angle(self, joint: int, direction: int | bool, speed: float | int) -> int:
        """M13 关节点动：关节 1–4（A–D）、方向（1 正向 / 0 反向）、速度（×100 编码，同 ``set_angle``）。"""
        return _write_ok(self.m13_continuous_joint(_pack_jog_axis_direction_speed_6(joint, direction, speed)))

    def set_jog_coord(self, axis: int, direction: int | bool, speed: float | int) -> int:
        """M14 坐标点动：轴 1–4（X,Y,Z,RX）、方向、速度（×100）。"""
        return _write_ok(self.m14_continuous_coordinate(_pack_jog_axis_direction_speed_6(axis, direction, speed)))

    def jog_increment_angle(self, joint: int, step_angle: float | int, speed: float | int) -> int:
        """M19 关节步进：关节 1–4、步进角度（度×100）、速度（×100）。"""
        return _write_ok(self.m19_step_joint(_pack_jog_axis_step_speed_6(joint, step_angle, speed)))

    def jog_increment_coord(self, axis: int, step: float | int, speed: float | int) -> int:
        """M20 坐标步进：轴 1–4、步进量（mm 等×100）、速度（×100）。"""
        return _write_ok(self.m20_step_coordinate(_pack_jog_axis_step_speed_6(axis, step, speed)))

    def set_estop(self) -> int:
        """M15."""
        return _write_ok(self.m15_estop())

    def set_relax_motors(self) -> int:
        """M17."""
        return _write_ok(self.m17_relax_motors())

    def set_brake_motors(self) -> int:
        """M18."""
        return _write_ok(self.m18_brake_motors())

    def set_rgb(self, r: int, g: int, b: int) -> int:
        """M23."""
        return _write_ok(self.m23_rgb(RgbColor(r, g, b)))

    def set_zero_calibration(self, joint_index: int) -> int:
        """M30."""
        return _write_ok(self.m30_zero_calibration(joint_index))

    def set_encoder_calibration_j1(self) -> int:
        """M31."""
        return _write_ok(self.m31_encoder_calibration_j1())

    def set_clear_zero_calibration(self, joint_index: int) -> int:
        """M32."""
        return _write_ok(self.m32_clear_zero_calibration(joint_index))

    def set_buzzer(self, on: bool) -> int:
        """M34."""
        return _write_ok(self.m34_buzzer(on))

    def set_end_button_enable(self) -> int:
        """M35."""
        return _write_ok(self.m35_enable_end_button())

    def set_end_button_disable(self) -> int:
        """M36."""
        return _write_ok(self.m36_disable_end_button())

    def set_force_homing(self) -> int:
        """M37."""
        return _write_ok(self.m37_force_homing())

    def set_conveyor(self, payload10: Sequence[int]) -> int:
        """M38."""
        return _write_ok(self.m38_conveyor(ConveyorParams(_bytes_u8(payload10, 10, label="payload10"))))

    def set_clear_errors(self) -> int:
        """M40."""
        return _write_ok(self.m40_clear_errors())

    def set_gripper_angle(self, angle_centideg: int, speed_centideg: int) -> int:
        """M25."""
        return _write_ok(self.m25_gripper_angle(angle_centideg, speed_centideg))

    def set_gripper_params(self, j: int, k: int, l_val: int) -> int:
        """M24 (parameter L)."""
        return _write_ok(self.m24_set_gripper_params(GripperParams(j & 0xFFFF, k & 0xFFFF, l_val & 0xFFFF)))

    def set_gripper_enable(self, enable: bool) -> int:
        """M28."""
        return _write_ok(self.m28_gripper_enable(enable))

    def set_gripper_zero_calibration(self) -> int:
        """M29."""
        return _write_ok(self.m29_gripper_zero_calibration())

    def set_pump(self, on_mask: int) -> int:
        """M70."""
        return _write_ok(self.m70_pump(on_mask))

    def set_base_io(self, payload6: Sequence[int]) -> int:
        """M60."""
        return _write_ok(self.m60_set_base_io(_bytes_u8(payload6, 6, label="payload6")))

    def set_tool_io(self, payload4: Sequence[int]) -> int:
        """M62."""
        return _write_ok(self.m62_set_tool_io(_bytes_u8(payload4, 4, label="payload4")))

    def set_laser_switch(self, on: bool) -> int:
        """M80."""
        return _write_ok(self.m80_laser_switch(on))

    def set_laser_pwm(self, level: int) -> int:
        """M81."""
        return _write_ok(self.m81_laser_pwm(level))

    def set_custom_pwm_switch(self, on: bool) -> int:
        """M82."""
        return _write_ok(self.m82_custom_pwm_switch(on))

    def set_custom_pwm_level(self, level: int) -> int:
        """M83."""
        return _write_ok(self.m83_custom_pwm_level(level))

    def set_stm32_fw_update_request(self) -> int:
        """G11."""
        return _write_ok(self.g11_request_stm32_fw_update())
