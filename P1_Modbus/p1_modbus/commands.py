"""High-level P1 protocol methods (G/M series)."""

from __future__ import annotations

import struct

from p1_modbus.client import P1ClientBase
from p1_modbus.errors import ProtocolError
from p1_modbus.models import ConveyorParams, GripperParams, PreviewPose, RgbColor

SLAVE = 0x2E
FC_READ = 0x03
FC_WRITE = 0x10


def _pack_u16_be(v: int) -> bytes:
    return struct.pack(">H", v & 0xFFFF)


def _parse_p1_read_payload(resp: bytes) -> bytes:
    """
    Parse P1 read response: ``2E 03 AH AL BC D...`` + CRC.

    ``BC`` is a single-byte data length (not Modbus register count).
    """
    if len(resp) < 7 or resp[0] != SLAVE or resp[1] != FC_READ:
        raise ProtocolError(f"Invalid read response: {resp.hex()}")
    byte_count = resp[4]
    end = 5 + byte_count
    if len(resp) < end + 2:
        raise ProtocolError(f"Truncated read response: {resp.hex()}")
    return resp[5:end]


def _parse_write_payload(resp: bytes) -> bytes:
    """Return payload bytes after ``2E 10 00 AH AL`` (excluding CRC)."""
    if len(resp) < 7 or resp[0] != SLAVE or resp[1] != FC_WRITE:
        raise ProtocolError(f"Invalid write response: {resp.hex()}")
    return resp[5:-2]


def _write_p10(addr: int, byte_count: int, data: bytes) -> bytes:
    if len(data) != byte_count:
        raise ValueError("data length must equal byte_count")
    ah, al = (addr >> 8) & 0xFF, addr & 0xFF
    return bytes([SLAVE, FC_WRITE, ah, al, byte_count & 0xFF]) + data


def _read_p03(addr: int, tail: bytes = b"") -> bytes:
    ah, al = (addr >> 8) & 0xFF, addr & 0xFF
    return bytes([SLAVE, FC_READ, ah, al]) + tail


def _payload_u16_be(d: bytes) -> int:
    """Interpret read payload as big-endian u16 (G6 ``00 0A``→10, G7 ``00 05``→5)."""
    if len(d) >= 2:
        return int.from_bytes(d[:2], "big")
    if len(d) == 1:
        return int(d[0])
    raise ProtocolError(f"Empty payload: {d.hex()}")


class P1CommandsMixin:
    """Protocol helpers mixed into :class:`P1Client`."""

    # --- G6 / G7 firmware (STM32) ---
    def read_main_fw_version(self) -> int:
        """G6: firmware version from 2-byte payload as big-endian u16 (e.g. ``00 0A`` → 10)."""
        r = self.request(_read_p03(0x0001, b"\x00"), expect_fc=FC_READ)
        d = _parse_p1_read_payload(r)
        if len(d) < 1:
            raise ProtocolError(f"Unexpected G6 payload: {d.hex()}")
        return _payload_u16_be(d)

    def read_main_fw_patch(self) -> int:
        """G7: correction / patch version (payload is 2 bytes, big-endian u16, e.g. ``00 05`` → 5)."""
        r = self.request(_read_p03(0x0002, b"\x00"), expect_fc=FC_READ)
        d = _parse_p1_read_payload(r)
        if len(d) < 1:
            raise ProtocolError(f"Unexpected G7 payload: {d.hex()}")
        return _payload_u16_be(d)

    # --- motion / control (FC 0x10) ---
    def g0_coordinate_max_speed(self, payload10: bytes) -> bytes:
        """G0 coordinate control at maximum speed (10 payload bytes)."""
        if len(payload10) != 10:
            raise ValueError("payload10 must be 10 bytes")
        return self.request(_write_p10(0x0003, 10, payload10), expect_fc=FC_WRITE)

    def g1_coordinate_fixed_speed(self, payload10: bytes) -> bytes:
        """G1 coordinate control at specified speed."""
        if len(payload10) != 10:
            raise ValueError("payload10 must be 10 bytes")
        return self.request(_write_p10(0x0004, 10, payload10), expect_fc=FC_WRITE)

    def g1_joint(self, payload10: bytes) -> bytes:
        """G1 joint control."""
        if len(payload10) != 10:
            raise ValueError("payload10 must be 10 bytes")
        return self.request(_write_p10(0x0005, 10, payload10), expect_fc=FC_WRITE)

    def g1_single_coordinate(self, payload6: bytes) -> bytes:
        if len(payload6) != 6:
            raise ValueError("payload6 must be 6 bytes")
        return self.request(_write_p10(0x0006, 6, payload6), expect_fc=FC_WRITE)

    def g1_single_joint(self, payload6: bytes) -> bytes:
        if len(payload6) != 6:
            raise ValueError("payload6 must be 6 bytes")
        return self.request(_write_p10(0x0007, 6, payload6), expect_fc=FC_WRITE)

    def g10_reboot_stm32(self) -> bytes:
        return self.request(_write_p10(0x0008, 0, b""), expect_fc=FC_WRITE)

    def m5_unlock(self) -> bytes:
        return self.request(_write_p10(0x0009, 0, b""), expect_fc=FC_WRITE)

    def m13_continuous_joint(self, payload6: bytes) -> bytes:
        if len(payload6) != 6:
            raise ValueError("payload6 must be 6 bytes")
        return self.request(_write_p10(0x000A, 6, payload6), expect_fc=FC_WRITE)

    def m14_continuous_coordinate(self, payload6: bytes) -> bytes:
        if len(payload6) != 6:
            raise ValueError("payload6 must be 6 bytes")
        return self.request(_write_p10(0x000B, 6, payload6), expect_fc=FC_WRITE)

    def m19_step_joint(self, payload6: bytes) -> bytes:
        if len(payload6) != 6:
            raise ValueError("payload6 must be 6 bytes")
        return self.request(_write_p10(0x000C, 6, payload6), expect_fc=FC_WRITE)

    def m20_step_coordinate(self, payload6: bytes) -> bytes:
        if len(payload6) != 6:
            raise ValueError("payload6 must be 6 bytes")
        return self.request(_write_p10(0x000D, 6, payload6), expect_fc=FC_WRITE)

    def m15_estop(self) -> bytes:
        return self.request(_write_p10(0x000F, 0, b""), expect_fc=FC_WRITE)

    def m17_relax_motors(self) -> bytes:
        return self.request(_write_p10(0x0010, 0, b""), expect_fc=FC_WRITE)

    def m18_brake_motors(self) -> bytes:
        return self.request(_write_p10(0x0011, 0, b""), expect_fc=FC_WRITE)

    def m22_read_motor_status(self) -> tuple[int, int, int, int, int]:
        r = self.request(_read_p03(0x0012, b"\x00"), expect_fc=FC_READ)
        d = _parse_p1_read_payload(r)
        if len(d) < 5:
            raise ProtocolError(f"Unexpected M22 payload: {d.hex()}")
        return tuple(int(x) for x in d[:5])

    def m23_rgb(self, color: RgbColor) -> bytes:
        payload = _pack_u16_be(color.r) + _pack_u16_be(color.g) + _pack_u16_be(color.b)
        return self.request(_write_p10(0x0013, 6, payload), expect_fc=FC_WRITE)

    def m30_zero_calibration(self, joint_index: int) -> bytes:
        payload = bytes([0x00, joint_index & 0xFF])
        return self.request(_write_p10(0x0014, 2, payload), expect_fc=FC_WRITE)

    def m31_encoder_calibration_j1(self) -> bytes:
        return self.request(_write_p10(0x0015, 0, b""), expect_fc=FC_WRITE)

    def m32_clear_zero_calibration(self, joint_index: int) -> bytes:
        payload = bytes([0x00, joint_index & 0xFF])
        return self.request(_write_p10(0x0016, 2, payload), expect_fc=FC_WRITE)

    def m34_buzzer(self, on: bool) -> bytes:
        payload = bytes([0x00, 0x01 if on else 0x00])
        return self.request(_write_p10(0x0017, 2, payload), expect_fc=FC_WRITE)

    def m35_enable_end_button(self) -> bytes:
        return self.request(_write_p10(0x0018, 0, b""), expect_fc=FC_WRITE)

    def m36_disable_end_button(self) -> bytes:
        return self.request(_write_p10(0x0019, 0, b""), expect_fc=FC_WRITE)

    def m37_force_homing(self) -> bytes:
        return self.request(_write_p10(0x001A, 0, b""), expect_fc=FC_WRITE)

    def m38_conveyor(self, params: ConveyorParams) -> bytes:
        return self.request(_write_p10(0x001B, 10, params.payload), expect_fc=FC_WRITE)

    def m40_clear_errors(self) -> bytes:
        return self.request(_write_p10(0x001C, 0, b""), expect_fc=FC_WRITE)

    def m51_preview(self, pose: PreviewPose) -> bool:
        """
        M51 preview mode.

        Returns True when the payload byte pair after ``BC`` is ``00 01`` (example: target reachable).
        """
        pdu = _read_p03(0x001D, bytes([0x08]) + pose.payload)
        r = self.request(pdu, expect_fc=FC_READ)
        d = _parse_p1_read_payload(r)
        if len(d) < 2:
            raise ProtocolError(f"Unexpected M51 payload: {d.hex()}")
        return d[0] == 0x00 and d[1] == 0x01

    def m119_read_zero_calibration_state(self) -> tuple[int, int, int, int]:
        r = self.request(_read_p03(0x001F, b"\x00"), expect_fc=FC_READ)
        d = _parse_p1_read_payload(r)
        if len(d) < 4:
            raise ProtocolError(f"Unexpected M119 payload: {d.hex()}")
        return int(d[0]), int(d[1]), int(d[2]), int(d[3])

    def m50_read_gripper_angle_centideg(self) -> int:
        """M50: raw u16; host divides by 100 for degrees per protocol note."""
        r = self.request(_read_p03(0x0020, b"\x00"), expect_fc=FC_READ)
        d = _parse_p1_read_payload(r)
        if len(d) < 2:
            raise ProtocolError(f"Unexpected M50 payload: {d.hex()}")
        return int.from_bytes(d[:2], "big")

    def m25_gripper_angle(self, angle_centideg: int, speed_centideg: int) -> bytes:
        payload = _pack_u16_be(angle_centideg) + _pack_u16_be(speed_centideg)
        return self.request(_write_p10(0x0021, 4, payload), expect_fc=FC_WRITE)

    def m24_set_gripper_params(self, p: GripperParams) -> bytes:
        payload = _pack_u16_be(p.j) + _pack_u16_be(p.k) + _pack_u16_be(p.l)
        return self.request(_write_p10(0x0022, 6, payload), expect_fc=FC_WRITE)

    def m26_read_gripper_params(self, p: GripperParams) -> int:
        """M26: sends J/K selector payload; returns raw u16 from device."""
        payload = _pack_u16_be(p.j) + _pack_u16_be(p.k)
        pdu = _read_p03(0x0023, bytes([0x04]) + payload)
        r = self.request(pdu, expect_fc=FC_READ)
        d = _parse_p1_read_payload(r)
        if len(d) < 2:
            raise ProtocolError(f"Unexpected M26 payload: {d.hex()}")
        return int.from_bytes(d[:2], "big")

    def m27_read_gripper_motion_state(self) -> int:
        r = self.request(_read_p03(0x0024, b"\x00"), expect_fc=FC_READ)
        d = _parse_p1_read_payload(r)
        if len(d) < 2:
            raise ProtocolError(f"Unexpected M27 payload: {d.hex()}")
        return int.from_bytes(d[:2], "big")

    def m28_gripper_enable(self, enable: bool) -> bytes:
        payload = bytes([0x00, 0x01 if enable else 0x00])
        return self.request(_write_p10(0x0025, 2, payload), expect_fc=FC_WRITE)

    def m29_gripper_zero_calibration(self) -> bytes:
        return self.request(_write_p10(0x0026, 0, b""), expect_fc=FC_WRITE)

    def m70_pump(self, on_mask: int) -> bytes:
        payload = bytes([0x00, on_mask & 0xFF])
        return self.request(_write_p10(0x0027, 2, payload), expect_fc=FC_WRITE)

    def m60_set_base_io(self, payload6: bytes) -> bytes:
        if len(payload6) != 6:
            raise ValueError("payload6 must be 6 bytes")
        return self.request(_write_p10(0x0028, 6, payload6), expect_fc=FC_WRITE)

    def m61_read_base_io(self) -> bytes:
        r = self.request(_read_p03(0x0029, b"\x00"), expect_fc=FC_READ)
        return _parse_p1_read_payload(r)

    def m62_set_tool_io(self, payload4: bytes) -> bytes:
        if len(payload4) != 4:
            raise ValueError("payload4 must be 4 bytes")
        return self.request(_write_p10(0x002A, 4, payload4), expect_fc=FC_WRITE)

    def m63_read_tool_io(self) -> bytes:
        r = self.request(_read_p03(0x002B, b"\x00"), expect_fc=FC_READ)
        return _parse_p1_read_payload(r)

    def m80_laser_switch(self, on: bool) -> bytes:
        payload = bytes([0x00, 0x01 if on else 0x00])
        return self.request(_write_p10(0x002C, 2, payload), expect_fc=FC_WRITE)

    def m81_laser_pwm(self, level: int) -> bytes:
        payload = bytes([0x00, level & 0xFF])
        return self.request(_write_p10(0x002D, 2, payload), expect_fc=FC_WRITE)

    def m82_custom_pwm_switch(self, on: bool) -> bytes:
        payload = bytes([0x00, 0x01 if on else 0x00])
        return self.request(_write_p10(0x002E, 2, payload), expect_fc=FC_WRITE)

    def m83_custom_pwm_level(self, level: int) -> bytes:
        payload = bytes([0x00, level & 0xFF])
        return self.request(_write_p10(0x002F, 2, payload), expect_fc=FC_WRITE)

    # --- display / extended bus (middle address byte ``0x01``) ---
    def read_display_fw_version(self) -> int:
        """M401: screen firmware version from 2-byte payload as big-endian u16 (e.g. ``00 0C`` → 12)."""
        r = self.request(bytes([SLAVE, FC_READ, 0x01, 0x01, 0x00]), expect_fc=FC_READ)
        d = _parse_p1_read_payload(r)
        if len(d) < 1:
            raise ProtocolError(f"Unexpected M401 payload: {d.hex()}")
        return _payload_u16_be(d)

    def read_display_fw_patch(self) -> int:
        """M402: screen correction version (2-byte payload as big-endian u16 when present)."""
        r = self.request(bytes([SLAVE, FC_READ, 0x01, 0x02, 0x00]), expect_fc=FC_READ)
        d = _parse_p1_read_payload(r)
        if len(d) < 1:
            raise ProtocolError(f"Unexpected M402 payload: {d.hex()}")
        return _payload_u16_be(d)

    def m405_read_angles(self) -> bytes:
        r = self.request(bytes([SLAVE, FC_READ, 0x01, 0x04, 0x00]), expect_fc=FC_READ)
        return _parse_p1_read_payload(r)

    def m406_read_coordinates(self) -> bytes:
        r = self.request(bytes([SLAVE, FC_READ, 0x01, 0x05, 0x00]), expect_fc=FC_READ)
        return _parse_p1_read_payload(r)

    def g8_read_errors(self) -> bytes:
        r = self.request(bytes([SLAVE, FC_READ, 0x01, 0x06, 0x00]), expect_fc=FC_READ)
        return _parse_p1_read_payload(r)

    def m200_read_main_runtime_state(self) -> int:
        r = self.request(bytes([SLAVE, FC_READ, 0x01, 0x07, 0x00]), expect_fc=FC_READ)
        d = _parse_p1_read_payload(r)
        if len(d) < 1:
            raise ProtocolError(f"Unexpected M200 payload: {d.hex()}")
        return int(d[0])

    def g11_request_stm32_fw_update(self) -> bytes:
        return self.request(bytes([SLAVE, FC_WRITE, 0x01, 0x08, 0x00]), expect_fc=FC_WRITE)

    def m600_read_motion_buffer_size(self) -> int:
        r = self.request(bytes([SLAVE, FC_READ, 0x01, 0x09, 0x00]), expect_fc=FC_READ)
        d = _parse_p1_read_payload(r)
        if len(d) < 2:
            raise ProtocolError(f"Unexpected M600 payload: {d.hex()}")
        return int.from_bytes(d[:2], "big")


class P1Client(P1ClientBase, P1CommandsMixin):
    """Concrete serial client with all P1 command helpers."""
