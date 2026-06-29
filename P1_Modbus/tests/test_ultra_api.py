import struct
from types import SimpleNamespace

import pytest

from p1_modbus.modbus_rtu import decode_u8_list
from p1_modbus.crc import append_crc
from p1_modbus.ultra_api import (
    UltraArmP1Modbus,
    _pack_axis_value_speed_6,
    _pack_jog_dir_6,
    _pack_jog_step_6,
)


def test_u8_helpers() -> None:
    assert decode_u8_list(b"\x01\x02") == [1, 2]
    assert struct.unpack(">h", b"\x00\x64")[0] == 100


def test_pack_jog_axis_direction_speed_6() -> None:
    # 关节1 正向 速度100
    assert _pack_jog_dir_6(1, 1, 100) == bytes.fromhex("000100012710")
    assert _pack_jog_dir_6(2, False, 50) == bytes.fromhex("000200001388")


def test_pack_jog_axis_step_speed_6() -> None:
    assert _pack_jog_step_6(1, 0.5, 100) == bytes.fromhex("000100322710")


def test_pack_axis_value_speed_6() -> None:
    # 关节 1、0°、速度 100 → 与协议示例一致
    assert _pack_axis_value_speed_6(1, 0, 100) == bytes.fromhex("000100002710")
    assert _pack_axis_value_speed_6(1, 10, 100) == bytes.fromhex("000103e82710")
    assert _pack_axis_value_speed_6(4, -1.5, 50) == struct.pack(
        ">hhh", 4, int(round(-1.5 * 100)), int(round(50 * 100))
    )


def test_pack_skips_limits_when_validate_false() -> None:
    with pytest.raises(ValueError):
        _pack_jog_dir_6(1, 1, 0, validate=True)
    _pack_jog_dir_6(1, 1, 0, validate=False)


def test_ultra_api_logs_tx_rx(capsys: pytest.CaptureFixture[str]) -> None:
    bot = UltraArmP1Modbus("COM99", debug=True)
    bot._ser = SimpleNamespace(
        is_open=True,
        in_waiting=0,
        write=lambda data: len(data),
        read=lambda n: b"",
        flush=lambda: None,
        close=lambda: None,
    )

    rsp = append_crc(bytes.fromhex("2E030001020102"))
    bot._rx.extend(rsp)

    pdu = bytes.fromhex("2E03000100")
    out = bot.request(pdu, expect_fc=0x03)
    assert out == rsp

    captured = capsys.readouterr()
    assert "TX" in captured.err
    assert "RX" in captured.err

    bot.close()
