from p1_modbus.crc import append_crc
from p1_modbus.framing import pop_first_frame


def test_pop_first_frame_single() -> None:
    pdu = bytes.fromhex("2E03000100")
    frame = append_crc(pdu)
    buf = bytearray(frame)
    out = pop_first_frame(buf)
    assert out == frame
    assert len(buf) == 0


def test_pop_first_frame_two_back_to_back() -> None:
    f1 = append_crc(bytes.fromhex("2E03000100"))
    f2 = append_crc(bytes.fromhex("2E10000800"))
    buf = bytearray(f1 + f2)
    assert pop_first_frame(buf) == f1
    assert pop_first_frame(buf) == f2
    assert len(buf) == 0


def test_pop_first_frame_strips_leading_noise() -> None:
    f1 = append_crc(bytes.fromhex("2E03000100"))
    buf = bytearray(b"\x00\xFF" + f1)
    assert pop_first_frame(buf) == f1
    assert len(buf) == 0


def test_pop_first_frame_partial() -> None:
    f1 = append_crc(bytes.fromhex("2E03000100"))
    buf = bytearray(f1[:4])
    assert pop_first_frame(buf) is None
    assert buf == bytearray(f1[:4])
