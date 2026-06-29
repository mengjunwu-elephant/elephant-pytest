"""P1 G/M 指令封装 — 直接组帧（风格对齐 Pro450，无寄存器表）."""

from __future__ import annotations

from p1_modbus.command_address import CommandAddress as A
from p1_modbus.modbus_rtu import ModbusRTU
from p1_modbus.models import (
    BaseIoOutput,
    ConveyorControl,
    ConveyorParams,
    DigitalIoOutput,
    GripperParams,
    KinematicsInput,
    PreviewPose,
    RgbColor,
)
from p1_modbus import modbus_rtu as pdu


class P1Client(ModbusRTU):
    """UltraArm P1 串口客户端：全部 G/M 底层方法。"""

    # --- firmware ---
    def read_main_fw_version(self) -> int:
        return pdu.decode_u16_be(self.read_p1(A.G6))

    def read_main_fw_patch(self) -> int:
        return pdu.decode_u16_be(self.read_p1(A.G7))

    # --- motion / control ---
    def g0_coordinate_max_speed(self, payload10: bytes) -> bytes:
        return self.write_p1(A.G0, pdu.require_payload(payload10, 10))

    def g1_coordinate_fixed_speed(self, payload10: bytes) -> bytes:
        return self.write_p1(A.G1_COORD, pdu.require_payload(payload10, 10))

    def g1_joint(self, payload10: bytes) -> bytes:
        return self.write_p1(A.G1_JOINT, pdu.require_payload(payload10, 10))

    def g1_single_coordinate(self, payload6: bytes) -> bytes:
        return self.write_p1(A.G1_SINGLE_COORD, pdu.require_payload(payload6, 6))

    def g1_single_joint(self, payload6: bytes) -> bytes:
        return self.write_p1(A.G1_SINGLE_JOINT, pdu.require_payload(payload6, 6))

    def g10_reboot_stm32(self) -> bytes:
        return self.write_p1(A.G10, b"")

    def m5_unlock(self) -> bytes:
        return self.write_p1(A.M5, b"")

    def m13_continuous_joint(self, payload6: bytes) -> bytes:
        return self.write_p1(A.M13, pdu.require_payload(payload6, 6))

    def m14_continuous_coordinate(self, payload6: bytes) -> bytes:
        return self.write_p1(A.M14, pdu.require_payload(payload6, 6))

    def m19_step_joint(self, payload6: bytes) -> bytes:
        return self.write_p1(A.M19, pdu.require_payload(payload6, 6))

    def m20_step_coordinate(self, payload6: bytes) -> bytes:
        return self.write_p1(A.M20, pdu.require_payload(payload6, 6))

    def m39_conveyor_stop(self) -> bytes:
        return self.write_p1(A.M39, b"")

    def m15_estop(self) -> bytes:
        return self.write_p1(A.M15, b"")

    def m17_relax_motors(self, joint_index: int = 0) -> bytes:
        return self.write_p1(A.M17, pdu.encode_joint_index(joint_index))

    def m18_brake_motors(self, joint_index: int = 0) -> bytes:
        return self.write_p1(A.M18, pdu.encode_joint_index(joint_index))

    def m22_read_motor_status(self) -> tuple[int, int, int, int, int]:
        return pdu.decode_u8_tuple5(self.read_p1(A.M22))

    def m23_rgb(self, color: RgbColor) -> bytes:
        return self.write_p1(A.M23, color.to_wire_bytes())

    def m30_zero_calibration(self, joint_index: int) -> bytes:
        return self.write_p1(A.M30, pdu.encode_joint_index(joint_index))

    def m31_encoder_calibration_j1(self) -> bytes:
        return self.write_p1(A.M31, b"")

    def m32_clear_zero_calibration(self, joint_index: int) -> bytes:
        return self.write_p1(A.M32, pdu.encode_joint_index(joint_index))

    def m34_buzzer(self, on: bool) -> bytes:
        return self.write_p1(A.M34, pdu.encode_bool_u16(on))

    def m35_enable_end_button(self) -> bytes:
        return self.write_p1(A.M35, b"")

    def m36_disable_end_button(self) -> bytes:
        return self.write_p1(A.M36, b"")

    def m37_force_homing(self) -> bytes:
        return self.write_p1(A.M37, b"")

    def m38_conveyor(self, params: ConveyorParams | ConveyorControl) -> bytes:
        data = params.to_wire_bytes() if isinstance(params, ConveyorControl) else params.payload
        return self.write_p1(A.M38, pdu.require_payload(data, 10))

    def m40_clear_errors(self) -> bytes:
        return self.write_p1(A.M40, b"")

    def m51_preview(self, pose: PreviewPose) -> bool:
        tail = pdu.kinematics_read_tail(pose.payload)
        return pdu.decode_preview_ok(self.read_p1(A.M51, tail))

    def m46_inverse_solution(self, kin: KinematicsInput | PreviewPose) -> list[float]:
        strict = self.validate_limits
        if isinstance(kin, KinematicsInput):
            data8 = kin.to_wire_bytes(strict=strict)
        else:
            data8 = kin.payload
        tail = pdu.kinematics_read_tail(data8)
        return pdu.decode_i16_centideg_list(self.read_p1(A.M46, tail))

    def m47_forward_solution(self, kin: KinematicsInput | PreviewPose) -> list[float]:
        strict = self.validate_limits
        if isinstance(kin, KinematicsInput):
            data8 = kin.to_wire_bytes(strict=strict)
        else:
            data8 = kin.payload
        tail = pdu.kinematics_read_tail(data8)
        return pdu.decode_i16_centideg_list(self.read_p1(A.M47, tail))

    def m84_read_pwm_status(self) -> list[int]:
        return pdu.decode_pwm_status(self.read_p1(A.M84))

    def m119_read_zero_calibration_state(self) -> tuple[int, int, int, int]:
        return pdu.decode_u8_tuple4(self.read_p1(A.M119))

    def m50_read_gripper_angle(self) -> int:
        return pdu.decode_u16_be(self.read_p1(A.M50))

    def m25_gripper_angle(self, angle: int, speed: int) -> bytes:
        return self.write_p1(A.M25, pdu.encode_gripper_angle(angle, speed))

    def m24_set_gripper_params(self, p: GripperParams) -> bytes:
        return self.write_p1(A.M24, p.to_wire_bytes())

    def m26_read_gripper_params(self, p: GripperParams) -> int:
        tail = pdu.gripper_read_tail(p.j, p.k)
        return pdu.decode_u16_be(self.read_p1(A.M26, tail))

    def m27_read_gripper_motion_state(self) -> int:
        return pdu.decode_u16_be(self.read_p1(A.M27))

    def m28_gripper_enable(self, enable: bool) -> bytes:
        return self.write_p1(A.M28, pdu.encode_bool_u16(enable))

    def m29_gripper_zero_calibration(self) -> bytes:
        return self.write_p1(A.M29, b"")

    def m70_pump(self, pump_state: int) -> bytes:
        return self.write_p1(A.M70, pdu.encode_u8_mask(pump_state))

    def m60_set_base_io(self, payload6: bytes | BaseIoOutput) -> bytes:
        data = payload6.to_wire_bytes() if isinstance(payload6, BaseIoOutput) else payload6
        return self.write_p1(A.M60, pdu.require_payload(data, 6))

    def m61_read_base_io(self) -> bytes:
        return bytes(self.read_p1(A.M61))

    def m62_set_tool_io(self, payload4: bytes | DigitalIoOutput) -> bytes:
        data = payload4.to_wire_bytes() if isinstance(payload4, DigitalIoOutput) else payload4
        return self.write_p1(A.M62, pdu.require_payload(data, 4))

    def m63_read_tool_io(self) -> bytes:
        return bytes(self.read_p1(A.M63))

    def m80_laser_switch(self, on: bool) -> bytes:
        return self.write_p1(A.M80, pdu.encode_bool_u16(on))

    def m81_laser_pwm(self, level: int) -> bytes:
        return self.write_p1(A.M81, pdu.encode_u16_level(level))

    def m82_custom_pwm_switch(self, on: bool) -> bytes:
        return self.write_p1(A.M82, pdu.encode_bool_u16(on))

    def m83_custom_pwm_level(self, level: int) -> bytes:
        return self.write_p1(A.M83, pdu.encode_u16_level(level))

    def read_display_fw_version(self) -> int:
        return pdu.decode_u16_be(self.read_p1(A.M401))

    def read_display_fw_patch(self) -> int:
        return pdu.decode_u16_be(self.read_p1(A.M402))

    def m405_read_angles(self) -> bytes:
        return pdu.float_list_to_centideg_bytes(pdu.decode_i16_centideg_list(self.read_p1(A.M405)))

    def m406_read_coordinates(self) -> bytes:
        return pdu.float_list_to_centideg_bytes(pdu.decode_i16_centideg_list(self.read_p1(A.M406)))

    def g8_read_errors(self) -> bytes:
        return bytes(self.read_p1(A.G8))

    def m200_read_main_runtime_state(self) -> int:
        return pdu.decode_u8(self.read_p1(A.M200))

    def g11_request_stm32_fw_update(self) -> bytes:
        return self.write_p1(A.G11, b"")

    def m600_read_motion_buffer_size(self) -> int:
        return pdu.decode_u16_be(self.read_p1(A.M600))
