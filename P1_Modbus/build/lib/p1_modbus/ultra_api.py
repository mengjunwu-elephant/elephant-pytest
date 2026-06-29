"""
UltraArm P1 Modbus 高层 API。

命名与参数语义对齐 ``docs/ultraArm_P1_zh.md``；底层为 ModbusRTU + CommandAddress + 直接组帧。

- **get_***：返回 ``int``、``list[int]`` 或 ``list[float]``
- **set_***：成功返回 ``0``（超时/协议错误抛异常）
"""

from __future__ import annotations

import logging
import struct
from collections.abc import Callable, Sequence
from typing import cast

from p1_modbus.commands import P1Client
from p1_modbus.command_address import CommandAddress as A
from p1_modbus.models import BaseIoOutput, ConveyorControl, DigitalIoOutput, GripperParams, KinematicsInput, RgbColor
from p1_modbus import ultra_api_limits as lim
from p1_modbus.modbus_rtu import centi_to_i16, decode_i16_centideg_list, decode_u8_list

# ---------------------------------------------------------------------------
# 组帧辅助（centi-units ×100，大端 int16）
# ---------------------------------------------------------------------------


def _to_centimil(x: float | int, *, strict: bool = True) -> int:
    return centi_to_i16(x, strict=strict)


def _is_sequence(obj: object) -> bool:
    return isinstance(obj, Sequence) and not isinstance(obj, (str, bytes))


def _pack_4_axes_speed_10(
    axes: Sequence[float | int],
    speed: float | int,
    *,
    validate: bool = True,
) -> bytes:
    if len(axes) != 4:
        raise ValueError("需要 4 个轴分量")
    lim.validate_if(validate, lim.validate_speed, speed)
    return struct.pack(
        ">hhhhh",
        _to_centimil(axes[0], strict=validate),
        _to_centimil(axes[1], strict=validate),
        _to_centimil(axes[2], strict=validate),
        _to_centimil(axes[3], strict=validate),
        _to_centimil(speed, strict=validate),
    )


def _pack_axis_value_speed_6(
    axis: int,
    value: float | int,
    speed: float | int,
    *,
    validate: bool = True,
) -> bytes:
    lim.validate_if(validate, lim.validate_axis_id, axis)
    lim.validate_if(validate, lim.validate_coord_axis, axis, value)
    lim.validate_if(validate, lim.validate_speed, speed)
    return struct.pack(
        ">hhh",
        axis,
        _to_centimil(value, strict=validate),
        _to_centimil(speed, strict=validate),
    )


def _pack_joint_value_speed_6(
    joint: int,
    angle: float | int,
    speed: float | int,
    *,
    validate: bool = True,
) -> bytes:
    lim.validate_if(validate, lim.validate_joint_angle, joint, angle)
    lim.validate_if(validate, lim.validate_speed, speed)
    return struct.pack(
        ">hhh",
        joint,
        _to_centimil(angle, strict=validate),
        _to_centimil(speed, strict=validate),
    )


def _pack_jog_dir_6(
    axis: int,
    direction: int | bool,
    speed: float | int,
    *,
    validate: bool = True,
) -> bytes:
    lim.validate_if(validate, lim.validate_axis_id, axis)
    lim.validate_if(validate, lim.validate_jog_direction, direction)
    lim.validate_if(validate, lim.validate_speed, speed)
    d = 1 if direction is True else 0 if direction is False else int(direction)
    return struct.pack(">hhh", axis, d, _to_centimil(speed, strict=validate))


def _pack_jog_step_6(
    axis: int,
    step: float | int,
    speed: float | int,
    *,
    validate: bool = True,
) -> bytes:
    lim.validate_if(validate, lim.validate_axis_id, axis)
    lim.validate_if(validate, lim.validate_speed, speed)
    return struct.pack(
        ">hhh",
        axis,
        _to_centimil(step, strict=validate),
        _to_centimil(speed, strict=validate),
    )


def _write_ok(_: bytes) -> int:
    return 0


class UltraArmP1Modbus(P1Client):
    """
    UltraArm P1 Modbus RTU 门面类，API 命名对齐 ``docs/ultraArm_P1_zh.md``。

    ``debug=True`` 时自动向 stderr 打印 TX/RX；首次收发自动打开串口。
    """

    def __init__(
        self,
        port: str,
        baudrate: int = 115200,
        timeout: float = 0.3,
        debug: bool = False,
        *,
        validate_limits: bool = True,
        write_timeout: float | None = None,
        event_hook: Callable[[bytes], None] | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        """
        Args:
            validate_limits: 为 ``False`` 时跳过 Python 侧物理量/范围校验，组帧时 int16
                按 16 位截断而非抛错（仍保留长度、类型等基础检查）。
        """
        super().__init__(
            port,
            baudrate,
            timeout,
            debug,
            validate_limits=validate_limits,
            write_timeout=write_timeout,
            event_hook=event_hook,
            logger=logger,
        )

    def _v(self, fn: Callable[..., None], /, *args, **kwargs) -> None:
        lim.validate_if(self.validate_limits, fn, *args, **kwargs)

    # --- 固件版本 ---
    def get_system_version(self) -> int:
        """读取固件主版本号（G6，Modbus ``0x0001``，u16 BE）。"""
        return int(self.read_main_fw_version())

    def get_modify_version(self) -> int:
        """读取固件更正版本号（G7，``0x0002``）。"""
        return int(self.read_main_fw_patch())

    def get_system_screen_version(self) -> int:
        """读取屏幕固件主版本号（M401，``0x0101``）。"""
        return int(self.read_display_fw_version())

    def get_modify_screen_version(self) -> int:
        """读取屏幕固件更正版本号（M402，``0x0102``）。"""
        return int(self.read_display_fw_patch())

    # --- 位姿 / 状态读 ---
    def get_angles_info(self) -> list[float]:
        """获取当前关节角 [J1..J4]（度）（M405，``0x0104``）。"""
        return decode_i16_centideg_list(self.read_p1(A.M405))

    def get_coords_info(self) -> list[float]:
        """获取当前坐标 [X,Y,Z,Rx]（mm/度）（M406，``0x0105``）。"""
        return decode_i16_centideg_list(self.read_p1(A.M406))

    def get_error_information(self) -> list[int]:
        """读取错误信息字节列表（G8，``0x0106``，32 位错误位）。"""
        return decode_u8_list(self.read_p1(A.G8))

    def get_run_status(self) -> int:
        """读取运行状态：0 静止，1 运动中（M200，``0x0107``）。"""
        return int(self.m200_read_main_runtime_state())

    def get_queue_size(self) -> int:
        """读取运动缓冲区队列大小（M600，``0x0109``）。"""
        return int(self.m600_read_motion_buffer_size())

    def get_motor_enable_status(self) -> list[int]:
        """读取五路电机使能状态（M22，``0x0012``）。"""
        return list(self.m22_read_motor_status())

    def get_zero_calibration_state(self, joint_number: int | None = None) -> list[int]:
        """
        读取零位校准状态，四关节 [0/1]（M119，``0x001F``）。

        Args:
            joint_number: 保留与文档一致；Modbus 固定返回四关节列表。
        """
        if joint_number is not None:
            self._v(lim.validate_joint_id, int(joint_number), allow_all=True)
        return list(self.m119_read_zero_calibration_state())

    def get_gripper_angle(self) -> int:
        """读取夹爪角度 1–100（M50，``0x0020``）。"""
        return int(self.m50_read_gripper_angle())

    def get_gripper_parameter(self, addr: int) -> int:
        """读取夹爪参数（M26，``0x0023``）。addr 范围 1–69。"""
        self._v(lim.validate_gripper_addr, addr)
        return int(self.m26_read_gripper_params(GripperParams(addr, 1, 0)))

    def get_all_base_io_states(self) -> list[int]:
        """读取底座 10 路 IO 状态 0–3（M61，``0x0029``）。"""
        return [int(b) for b in self.m61_read_base_io()]

    def get_base_io_state(self, pin_no: int) -> int:
        """读取单个底座 IO 引脚状态（pin 1–10）。"""
        self._v(lim.validate_base_io_pin, pin_no)
        states = self.get_all_base_io_states()
        if pin_no < 1 or pin_no > len(states):
            raise ValueError(f"pin_no {pin_no} 超出返回长度 {len(states)}")
        return int(states[pin_no - 1])

    def get_all_end_io_states(self) -> list[int]:
        """读取末端 4 路 IO 状态 0–3（M63，``0x002B``）。"""
        return [int(b) for b in self.m63_read_tool_io()]

    def get_end_io_state(self, pin_no: int) -> int:
        """读取单个末端 IO 引脚状态（pin 1–4）。"""
        self._v(lim.validate_end_io_pin, pin_no)
        states = self.get_all_end_io_states()
        return int(states[pin_no - 1])

    def get_pwm_status(self) -> list[int]:
        """
        读取 PWM 输出状态，长度 4（M84，``0x0032``）。

        [激光开关, 激光档位, 自定义开关, 自定义档位]
        """
        return list(self.m84_read_pwm_status())

    def coord_inverse_solution(self, coords: Sequence[float | int]) -> list[float]:
        """
        坐标逆解：输入 [X,Y,Z,R] 返回关节角（M46，``0x0033``）。

        Args:
            coords: 长度 4 的坐标列表，范围同 ``set_coords``。
        """
        if len(coords) != 4:
            raise ValueError("coords 长度须为 4")
        self._v(lim.validate_coords, coords)
        kin = KinematicsInput(tuple(float(c) for c in coords))
        return list(self.m46_inverse_solution(kin))

    def angle_correct_solution(self, angles: Sequence[float | int]) -> list[float]:
        """
        角度正解：输入 [J1..J4] 返回坐标（M47，``0x0034``）。

        Args:
            angles: 长度 4，各关节角范围见 ``set_angle``。
        """
        self._v(lim.validate_joint_angles, angles)
        kin = KinematicsInput(tuple(float(a) for a in angles))
        return list(self.m47_forward_solution(kin))

    # --- 运动写 ---
    def set_coords_max_speed(self, coords: Sequence[float | int]) -> int:
        """
        以最大速度发送坐标（G0，``0x0003``）。

        Args:
            coords: [X,Y,Z,Rx] 或 [X,Y,Z]（Rx 缺省为 0）。
        """
        cs = list(coords)
        if len(cs) == 3:
            cs.append(0.0)
        if len(cs) != 4:
            raise ValueError("coords 长度须为 3 或 4")
        self._v(lim.validate_coords, cs)
        payload = struct.pack(
            ">hhhhh",
            *(_to_centimil(c, strict=self.validate_limits) for c in cs),
            _to_centimil(lim.SPEED_RANGE[1], strict=self.validate_limits),
        )
        return _write_ok(self.g0_coordinate_max_speed(payload))

    def set_coords(
        self,
        x_or_axes: Sequence[float | int] | float | int,
        y_or_speed: float | int | None = None,
        z: float | int | None = None,
        rx: float | int | None = None,
        speed: float | int | None = None,
    ) -> int:
        """
        规定速度坐标运动（G1，``0x0004``）。

        Args:
            speed: 1–100。可 ``set_coords([x,y,z,rx], speed)`` 或五参数形式。
        """
        payload = self._motion_payload_4_speed(x_or_axes, y_or_speed, z, rx, speed)
        return _write_ok(self.g1_coordinate_fixed_speed(payload))

    def set_coord(
        self,
        coord_id: int,
        coord: float | int,
        speed: float | int,
    ) -> int:
        """单坐标运动（G1 单坐标，``0x0006``）。coord_id: 1=X,2=Y,3=Z,4=Rx；speed 1–100。"""
        return _write_ok(self.g1_single_coordinate(
            _pack_axis_value_speed_6(coord_id, coord, speed, validate=self.validate_limits)
        ))

    def set_angles(
        self,
        j1_or_axes: Sequence[float | int] | float | int,
        j2_or_speed: float | int | None = None,
        j3: float | int | None = None,
        j4: float | int | None = None,
        speed: float | int | None = None,
    ) -> int:
        """四关节运动（G1 关节，``0x0005``）。speed 范围 1–100。"""
        payload = self._motion_payload_4_speed(j1_or_axes, j2_or_speed, j3, j4, speed, joint=True)
        return _write_ok(self.g1_joint(payload))

    def set_angle(self, joint_id: int, angle: float | int, speed: float | int) -> int:
        """单关节运动（G1 单关节，``0x0007``）。joint_id 1–4；speed 1–100。"""
        return _write_ok(self.g1_single_joint(
            _pack_joint_value_speed_6(joint_id, angle, speed, validate=self.validate_limits)
        ))

    def _motion_payload_4_speed(
        self,
        a1,
        a2=None,
        a3=None,
        a4=None,
        speed=None,
        *,
        joint: bool = False,
    ) -> bytes:
        if _is_sequence(a1):
            if speed is not None:
                raise ValueError("列表形式勿再传 keyword speed")
            if a2 is None:
                raise ValueError("需要第二参数 speed")
            axes = cast(Sequence[float | int], a1)
            if len(axes) != 4:
                raise ValueError("需要 4 个分量")
            if joint:
                self._v(lim.validate_joint_angles, axes)
            else:
                self._v(lim.validate_coords, axes)
            return _pack_4_axes_speed_10(axes, a2, validate=self.validate_limits)
        if a2 is None or a3 is None or a4 is None or speed is None:
            raise ValueError("需要五个数值或 [四元组], speed")
        axes = (a1, a2, a3, a4)
        if joint:
            self._v(lim.validate_joint_angles, axes)
        else:
            self._v(lim.validate_coords, axes)
        return _pack_4_axes_speed_10(axes, speed, validate=self.validate_limits)

    def set_reboot(self) -> int:
        """重启 STM32（G10，``0x0008``）。"""
        return _write_ok(self.g10_reboot_stm32())

    def collision_unlock(self) -> int:
        """碰撞检测后解锁（M5，``0x0009``）。"""
        return _write_ok(self.m5_unlock())

    def stop(self) -> int:
        """停止运动（M15，``0x000F``）。"""
        return _write_ok(self.m15_estop())

    def set_joint_release(self, joint_id: int = 0) -> int:
        """放松关节（M17，``0x0010``）。joint_id 0–4（0=全部）。"""
        self._v(lim.validate_joint_id, joint_id, allow_all=True)
        return _write_ok(self.m17_relax_motors(joint_id))

    def set_joint_enable(self, joint_id: int = 0) -> int:
        """锁紧关节（M18，``0x0011``）。参数同 ``set_joint_release``。"""
        self._v(lim.validate_joint_id, joint_id, allow_all=True)
        return _write_ok(self.m18_brake_motors(joint_id))

    def set_jog_angle(self, joint_id: int, direction: int | bool, speed: float | int) -> int:
        """关节点动（M13，``0x000A``）。direction 0/1；speed 1–100。"""
        self._v(lim.validate_joint_id, joint_id, allow_all=False)
        return _write_ok(self.m13_continuous_joint(
            _pack_jog_dir_6(joint_id, direction, speed, validate=self.validate_limits)
        ))

    def set_jog_coord(self, axis_id: int, direction: int | bool, speed: float | int) -> int:
        """坐标点动（M14，``0x000B``）。"""
        return _write_ok(self.m14_continuous_coordinate(
            _pack_jog_dir_6(axis_id, direction, speed, validate=self.validate_limits)
        ))

    def jog_increment_angle(self, joint_id: int, increment: float | int, speed: float | int) -> int:
        """关节步进（M19，``0x000C``）。"""
        self._v(lim.validate_joint_id, joint_id, allow_all=False)
        return _write_ok(self.m19_step_joint(
            _pack_jog_step_6(joint_id, increment, speed, validate=self.validate_limits)
        ))

    def jog_increment_coord(self, coord_id: int, increment: float | int, speed: float | int) -> int:
        """坐标步进（M20，``0x000D``）。"""
        return _write_ok(self.m20_step_coordinate(
            _pack_jog_step_6(coord_id, increment, speed, validate=self.validate_limits)
        ))

    def set_color(self, r: int, g: int, b: int) -> int:
        """设置 RGB 灯色（M23，``0x0013``）。分量 0–255。"""
        self._v(lim.validate_rgb, r, g, b)
        return _write_ok(self.m23_rgb(RgbColor(r, g, b)))

    def set_zero_calibration(self, joint_number: int) -> int:
        """零位校准（M30，``0x0014``）。joint_number 0–4。"""
        self._v(lim.validate_joint_id, joint_number, allow_all=True)
        return _write_ok(self.m30_zero_calibration(joint_number))

    def set_encoder_calibration_j1(self) -> int:
        """J1 编码器校准（M31，``0x0015``）。"""
        return _write_ok(self.m31_encoder_calibration_j1())

    def set_clear_zero_calibration(self, joint_index: int) -> int:
        """清除零位校准状态（M32，``0x0016``）。joint 1–4。"""
        self._v(lim._in_range, "joint_index", joint_index, *lim.ZERO_CALIB_CLEAR_RANGE)
        return _write_ok(self.m32_clear_zero_calibration(joint_index))

    def set_buzzer(self, on: bool) -> int:
        """蜂鸣器（M34，``0x0017``）。"""
        return _write_ok(self.m34_buzzer(on))

    def set_end_button_enable(self) -> int:
        """末端按钮使能（M35）。"""
        return _write_ok(self.m35_enable_end_button())

    def set_end_button_disable(self) -> int:
        """末端按钮失能（M36）。"""
        return _write_ok(self.m36_disable_end_button())

    def forced_reset_zero(self) -> int:
        """强制回零（M37，``0x001A``）。"""
        return _write_ok(self.m37_force_homing())

    def set_conveyor_control(self, state: int, direction: int, speed: int, distance: int) -> int:
        """
        传送带控制（M38，``0x001B``）。

        Args:
            state: 0/1；direction: 0 前进/1 后退；speed: 50–500000；distance: 0–1200 mm。
        """
        self._v(lim.validate_conveyor, state, direction, speed, distance)
        ctrl = ConveyorControl(state, direction, speed, distance)
        return _write_ok(self.m38_conveyor(ctrl))

    def set_conveyor_stop(self) -> int:
        """传送带停止（M39，``0x000E``，地址待实机确认）。"""
        return _write_ok(self.m39_conveyor_stop())

    def set_preview_mode(self, coords: Sequence[float | int]) -> int:
        """
        坐标轨迹预览（M51，``0x001D``）。不可达时返回 ``1``。

        Args:
            coords: [X,Y,Z,R]，范围同 ``set_coords``。
        """
        from p1_modbus.models import PreviewPose

        if len(coords) != 4:
            raise ValueError("coords 长度须为 4")
        self._v(lim.validate_coords, coords)
        ok = self.m51_preview(PreviewPose.from_values(coords, strict=self.validate_limits))
        return 0 if ok else 1

    def clear_error_status(self) -> int:
        """清除错误状态（M40，``0x001C``）。"""
        return _write_ok(self.m40_clear_errors())

    def set_gripper_angle(self, gripper_angle: int, gripper_speed: int) -> int:
        """设置夹爪角度 1–100 与速度 1–100（M25）。"""
        self._v(lim.validate_gripper_angle, gripper_angle)
        self._v(lim.validate_gripper_speed, gripper_speed)
        return _write_ok(self.m25_gripper_angle(gripper_angle, gripper_speed))

    def set_gripper_parameter(self, addr: int, parameter_value: int) -> int:
        """设置夹爪参数（M24）。addr 1–69，值 0–65535。"""
        self._v(lim.validate_gripper_addr, addr)
        self._v(lim.validate_gripper_param_value, parameter_value)
        return _write_ok(self.m24_set_gripper_params(GripperParams(addr, 1, parameter_value)))

    def set_gripper_enable_status(self, state: int) -> int:
        """夹爪使能 0/1（M28）。"""
        self._v(lim._in_range, "state", state, 0, 1)
        return _write_ok(self.m28_gripper_enable(bool(state)))

    def set_gripper_zero(self) -> int:
        """夹爪零位校准（M29）。"""
        return _write_ok(self.m29_gripper_zero_calibration())

    def set_pump_state(self, pump_state: int) -> int:
        """吸泵状态 0 吸/1 吹/2 关（M70）。"""
        self._v(lim.validate_pump_state, pump_state)
        return _write_ok(self.m70_pump(pump_state))

    def set_base_io_output(self, pin_no: int, pin_status: int, pin_signal: int) -> int:
        """底座 IO 输出（M60）。pin 1–10；模式 0 入/1 出；电平 0/1。"""
        self._v(lim.validate_base_io_pin, pin_no)
        self._v(lim.validate_io_mode, pin_status)
        self._v(lim.validate_io_signal, pin_signal)
        return _write_ok(self.m60_set_base_io(BaseIoOutput(pin_no, pin_status, pin_signal)))

    def set_digital_io_output(self, pin_no: int, pin_signal: int) -> int:
        """末端数字 IO 输出（M62）。pin 3–4；电平 0/1。"""
        self._v(lim.validate_digital_output_pin, pin_no)
        self._v(lim.validate_io_signal, pin_signal)
        return _write_ok(self.m62_set_tool_io(DigitalIoOutput(pin_no, pin_signal)))

    def set_pwm_laser_mode(self, state: int) -> int:
        """激光 PWM 开关 0/1（M80）。"""
        self._v(lim.validate_pwm_mode, state)
        return _write_ok(self.m80_laser_switch(bool(state)))

    def set_pwm_laser(self, p_value: int) -> int:
        """激光 PWM 档位 0–255（M81）。"""
        self._v(lim.validate_pwm_level, p_value)
        return _write_ok(self.m81_laser_pwm(p_value))

    def set_pwm_custom_mode(self, state: int) -> int:
        """自定义 PWM 开关 0/1（M82）。"""
        self._v(lim.validate_pwm_mode, state)
        return _write_ok(self.m82_custom_pwm_switch(bool(state)))

    def set_pwm_custom(self, p_value: int) -> int:
        """自定义 PWM 档位 0–255（M83）。"""
        self._v(lim.validate_pwm_level, p_value)
        return _write_ok(self.m83_custom_pwm_level(p_value))

    def upgrade_restart(self) -> int:
        """固件升级重启请求（G11，``0x0108``）。"""
        return _write_ok(self.g11_request_stm32_fw_update())
