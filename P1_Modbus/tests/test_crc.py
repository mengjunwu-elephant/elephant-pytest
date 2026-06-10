from p1_modbus.crc import append_crc, crc16_modbus, crc16_modbus_bytes, verify_crc


def test_crc16_modbus_known_vector() -> None:
    # Classic Modbus RTU test vector: 01 03 00 00 00 01 -> CRC16 = 0x840A, on wire low byte first: 0A 84
    data = bytes.fromhex("010300000001")
    assert crc16_modbus(data) == 0x840A
    assert crc16_modbus_bytes(data) == bytes.fromhex("0A84")


def test_append_and_verify_p1_prefix() -> None:
    pdu = bytes.fromhex("2E03000100")
    frame = append_crc(pdu)
    assert verify_crc(frame)
    assert frame == pdu + crc16_modbus_bytes(pdu)


def test_verify_crc_rejects_garbage() -> None:
    assert not verify_crc(bytes.fromhex("2E03000100DEAD"))
