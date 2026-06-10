from p1_modbus.crc import append_crc
from p1_modbus.events import decode_collision_event, decode_limit_event


def test_decode_limit_event() -> None:
    pdu = bytes.fromhex("2E1000300101")
    frame = append_crc(pdu)
    assert decode_limit_event(frame) == (1, 1)


def test_decode_collision_event() -> None:
    pdu = bytes.fromhex("2E1000310102")
    frame = append_crc(pdu)
    assert decode_collision_event(frame) == (1, 2)
