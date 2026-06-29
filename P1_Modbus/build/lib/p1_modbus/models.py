"""Structured command parameters with wire encoding."""

from __future__ import annotations

import struct
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class RgbColor:
    """M23 RGB components (0–255 on wire as u16 BE each)."""

    r: int
    g: int
    b: int

    def to_wire_bytes(self) -> bytes:
        return struct.pack(">HHH", self.r & 0xFFFF, self.g & 0xFFFF, self.b & 0xFFFF)


@dataclass(frozen=True)
class PreviewPose:
    """Eight payload bytes for M51 / kinematics read tail (4× int16 BE centi-units)."""

    payload: bytes

    def __post_init__(self) -> None:
        if len(self.payload) != 8:
            raise ValueError("PreviewPose.payload must be exactly 8 bytes")

    @classmethod
    def from_values(
        cls,
        values: Sequence[float | int],
        *,
        strict: bool = True,
    ) -> PreviewPose:
        if len(values) != 4:
            raise ValueError("PreviewPose.from_values: need 4 numbers")
        from p1_modbus.modbus_rtu import centi_to_i16

        parts = [centi_to_i16(v, strict=strict) for v in values]
        return cls(struct.pack(">hhhh", *parts))


@dataclass(frozen=True)
class KinematicsInput:
    """M46/M47 read-request tail: four centi-units (degrees or mm)."""

    values: tuple[float, float, float, float]

    def to_wire_bytes(self, *, strict: bool = True) -> bytes:
        return PreviewPose.from_values(self.values, strict=strict).payload


@dataclass(frozen=True)
class GripperParams:
    """M24 / M26 J/K/L (16-bit BE on wire)."""

    j: int
    k: int
    l: int  # noqa: E741

    def to_wire_bytes(self) -> bytes:
        return struct.pack(">HHH", self.j & 0xFFFF, self.k & 0xFFFF, self.l & 0xFFFF)

    def to_read_selector_bytes(self) -> bytes:
        return struct.pack(">HH", self.j & 0xFFFF, self.k & 0xFFFF)


@dataclass(frozen=True)
class ConveyorControl:
    """M38: J/K u16, L u32 BE speed, S u16 distance (10 bytes)."""

    state: int
    direction: int
    speed: int
    distance: int

    def to_wire_bytes(self) -> bytes:
        return struct.pack(
            ">HHIH",
            self.state & 0xFFFF,
            self.direction & 0xFFFF,
            self.speed & 0xFFFFFFFF,
            self.distance & 0xFFFF,
        )


@dataclass(frozen=True)
class ConveyorParams:
    """Legacy raw 10-byte M38 payload."""

    payload: bytes

    def __post_init__(self) -> None:
        if len(self.payload) != 10:
            raise ValueError("ConveyorParams.payload must be exactly 10 bytes")


@dataclass(frozen=True)
class BaseIoOutput:
    """M60: P/K/S as three u16 BE (pin 1–10, mode 0/1, signal 0/1)."""

    pin_no: int
    pin_status: int
    pin_signal: int

    def to_wire_bytes(self) -> bytes:
        return struct.pack(">HHH", self.pin_no & 0xFFFF, self.pin_status & 0xFFFF, self.pin_signal & 0xFFFF)


@dataclass(frozen=True)
class DigitalIoOutput:
    """M62: P/S as two u16 BE (pin 3–4, signal 0/1)."""

    pin_no: int
    pin_signal: int

    def to_wire_bytes(self) -> bytes:
        return struct.pack(">HH", self.pin_no & 0xFFFF, self.pin_signal & 0xFFFF)
