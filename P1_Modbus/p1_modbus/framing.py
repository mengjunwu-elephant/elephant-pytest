"""Extract complete RTU frames from a byte stream using CRC validation."""

from __future__ import annotations

from p1_modbus.crc import verify_crc

SLAVE_ID = 0x2E
MIN_FRAME_LEN = 5  # slave + fc + at least 1 payload byte + crc16
MAX_FRAME_LEN = 512


def pop_first_frame(buf: bytearray) -> bytes | None:
    """
    Remove and return the first valid CRC-checked frame starting at SLAVE_ID,
    or None if no complete frame is available yet.

    Uses shortest-length match from MIN_FRAME_LEN upward to reduce the chance
    of mis-alignment eating into a following frame (CRC collision is unlikely).
    """
    while buf and buf[0] != SLAVE_ID:
        del buf[0]

    if len(buf) < MIN_FRAME_LEN:
        return None

    upper = min(len(buf), MAX_FRAME_LEN)
    for end in range(MIN_FRAME_LEN, upper + 1):
        candidate = bytes(buf[:end])
        if verify_crc(candidate):
            del buf[:end]
            return candidate
    return None
