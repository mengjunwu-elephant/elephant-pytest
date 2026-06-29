"""Golden payload / PDU encoding tests (modbus_rtu module)."""

import struct

import pytest

from p1_modbus.models import BaseIoOutput, ConveyorControl, DigitalIoOutput, PreviewPose, RgbColor
from p1_modbus.command_address import CommandAddress as A
from p1_modbus.crc import append_crc
from p1_modbus import modbus_rtu as pdu


def test_m38_conveyor_example() -> None:
    wire_bytes = ConveyorControl(1, 1, 1000, 0).to_wire_bytes()
    assert wire_bytes == bytes.fromhex("00010001000003E80000")


def test_m60_base_io_example() -> None:
    wire_bytes = BaseIoOutput(5, 0, 0).to_wire_bytes()
    assert wire_bytes == bytes.fromhex("000500000000")


def test_m62_tool_io_example() -> None:
    wire_bytes = DigitalIoOutput(3, 1).to_wire_bytes()
    assert wire_bytes == bytes.fromhex("00030001")


def test_m23_rgb_example() -> None:
    wire_bytes = RgbColor(50, 50, 50).to_wire_bytes()
    assert wire_bytes == bytes.fromhex("003200320032")


def test_m51_preview_coords_tail() -> None:
    tail = PreviewPose.from_values([223.5, 0.0, 50.0, 50.0]).payload
    assert len(tail) == 8


def test_g6_read_pdu() -> None:
    assert pdu.build_read_pdu(A.G6, b"\x00") == bytes.fromhex("2E03000100")


def test_m15_write_pdu_empty_payload() -> None:
    assert pdu.build_write_pdu(A.M15, b"") == bytes.fromhex("2E10000F00")


def test_m17_relax_motors_write_pdu() -> None:
    assert pdu.build_write_pdu(A.M17, pdu.encode_joint_index(0)) == bytes.fromhex(
        "2E100010020000"
    )
    assert pdu.build_write_pdu(A.M17, pdu.encode_joint_index(2)) == bytes.fromhex(
        "2E100010020002"
    )


def test_m18_brake_motors_write_pdu() -> None:
    assert pdu.build_write_pdu(A.M18, pdu.encode_joint_index(0)) == bytes.fromhex(
        "2E100011020000"
    )
    assert pdu.build_write_pdu(A.M18, pdu.encode_joint_index(1)) == bytes.fromhex(
        "2E100011020001"
    )


def test_g1_single_joint_write_pdu_example() -> None:
    payload = bytes.fromhex("000100002710")
    assert pdu.build_write_pdu(A.G1_SINGLE_JOINT, payload) == bytes.fromhex(
        "2E10000706000100002710"
    )


def test_decode_pwm_status_4_bytes() -> None:
    assert pdu.decode_pwm_status(bytes.fromhex("01640164")) == [1, 100, 1, 100]
    assert pdu.decode_pwm_status(bytes.fromhex("00000000")) == [0, 0, 0, 0]
    frame = append_crc(bytes.fromhex("2E0300320401640164"))
    assert pdu.decode_pwm_status(pdu.parse_read_payload(frame)) == [1, 100, 1, 100]


def test_centi_to_i16_non_strict_allows_large_coord() -> None:
    with pytest.raises(ValueError):
        pdu.centi_to_i16(350.0, strict=True)
    wrapped = pdu.centi_to_i16(350.0, strict=False)
    assert wrapped == struct.unpack(">h", struct.pack(">H", 35000))[0]
    from p1_modbus.models import KinematicsInput

    payload = KinematicsInput((350.0, 0.0, 90.0, 0.0)).to_wire_bytes(strict=False)
    assert payload[:2] == struct.pack(">h", wrapped)

