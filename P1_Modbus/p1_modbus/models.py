"""Small dataclasses for structured command parameters."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RgbColor:
    """RGB 0–100 (device uses centi-percent style payload; see M23 examples)."""

    r: int
    g: int
    b: int


@dataclass(frozen=True)
class PreviewPose:
    """Eight payload bytes for M51 preview (caller encodes floats/ints as required by firmware)."""

    payload: bytes

    def __post_init__(self) -> None:
        if len(self.payload) != 8:
            raise ValueError("PreviewPose.payload must be exactly 8 bytes")


@dataclass(frozen=True)
class GripperParams:
    """M24 / M26 style J/K/L parameters (16-bit fields, big-endian on wire)."""

    j: int
    k: int
    l: int  # noqa: E741


@dataclass(frozen=True)
class ConveyorParams:
    """M38 conveyor: 10-byte payload (see firmware layout)."""

    payload: bytes

    def __post_init__(self) -> None:
        if len(self.payload) != 10:
            raise ValueError("ConveyorParams.payload must be exactly 10 bytes")
