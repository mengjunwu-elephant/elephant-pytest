"""Decode auto-report frames (limit / collision)."""

SLAVE = 0x2E


def decode_limit_event(frame: bytes) -> tuple[int, int]:
    """
    Parse ``2E 10 00 30 ...`` frame body (excluding CRC).

    Returns ``(code, joint_or_axis)`` — exact semantics follow firmware; bytes
    are taken from positions 4 and 5 in the full frame (0-based).
    """
    if len(frame) < 8 or frame[0] != SLAVE or frame[1] != 0x10 or frame[2:4] != b"\x00\x30":
        raise ValueError(f"Not a limit event frame: {frame.hex()}")
    return int(frame[4]), int(frame[5])


def decode_collision_event(frame: bytes) -> tuple[int, int]:
    """Parse ``2E 10 00 31 ...``."""
    if len(frame) < 8 or frame[0] != SLAVE or frame[1] != 0x10 or frame[2:4] != b"\x00\x31":
        raise ValueError(f"Not a collision event frame: {frame.hex()}")
    return int(frame[4]), int(frame[5])
