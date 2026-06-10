"""Modbus RTU CRC16 (polynomial 0xA001, init 0xFFFF, little-endian on wire)."""


def crc16_modbus(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF


def crc16_modbus_bytes(data: bytes) -> bytes:
    """Return CRC as two bytes: low byte first (Modbus RTU convention)."""
    c = crc16_modbus(data)
    return bytes((c & 0xFF, (c >> 8) & 0xFF))


def append_crc(frame_without_crc: bytes) -> bytes:
    return frame_without_crc + crc16_modbus_bytes(frame_without_crc)


def verify_crc(frame_with_crc: bytes) -> bool:
    if len(frame_with_crc) < 3:
        return False
    body, crc_b = frame_with_crc[:-2], frame_with_crc[-2:]
    return crc16_modbus_bytes(body) == crc_b
