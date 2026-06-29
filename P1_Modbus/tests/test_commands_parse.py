from p1_modbus.modbus_rtu import parse_read_payload
from p1_modbus.crc import append_crc


def test_parse_read_payload_echoed_address() -> None:
    pdu = bytes.fromhex("2E03000102000C")  # BC=2, data 00 0C
    frame = append_crc(pdu)
    data = parse_read_payload(frame)
    assert data == bytes.fromhex("000C")


def test_parse_read_motor_status_shape() -> None:
    pdu = bytes.fromhex("2E030012050101010101")
    frame = append_crc(pdu)
    data = parse_read_payload(frame)
    assert data == bytes.fromhex("0101010101")
