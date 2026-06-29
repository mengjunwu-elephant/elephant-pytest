"""Modbus RTU transport + P1 PDU 组帧/解析（对齐 Pro450 单模块风格）."""

from __future__ import annotations

import logging
import struct
import threading
import time
from typing import Callable

import serial

from p1_modbus.crc import append_crc
from p1_modbus.errors import ProtocolError
from p1_modbus.framing import SLAVE_ID, pop_first_frame

FC_READ = 0x03
FC_WRITE = 0x10
SLAVE = SLAVE_ID


# ---------------------------------------------------------------------------
# P1 线格式工具（原 wire.py，与 ModbusRTU 同模块）
# ---------------------------------------------------------------------------


def build_read_pdu(addr: int, tail: bytes = b"\x00") -> bytes:
    ah, al = (addr >> 8) & 0xFF, addr & 0xFF
    return bytes([SLAVE, FC_READ, ah, al]) + tail


def build_write_pdu(addr: int, data: bytes) -> bytes:
    ah, al = (addr >> 8) & 0xFF, addr & 0xFF
    return bytes([SLAVE, FC_WRITE, ah, al, len(data) & 0xFF]) + data


def parse_read_payload(resp: bytes) -> bytes:
    """解析 ``2E 03 AH AL BC DATA...`` + CRC。"""
    if len(resp) < 7 or resp[0] != SLAVE or resp[1] != FC_READ:
        raise ProtocolError(f"Invalid read response: {resp.hex()}")
    byte_count = resp[4]
    end = 5 + byte_count
    if len(resp) < end + 2:
        raise ProtocolError(f"Truncated read response: {resp.hex()}")
    return resp[5:end]


def decode_u16_be(payload: bytes) -> int:
    if len(payload) < 2:
        raise ProtocolError(f"Expected u16 payload, got {payload.hex()}")
    return int.from_bytes(payload[:2], "big")


def decode_u8(payload: bytes) -> int:
    if not payload:
        raise ProtocolError("Empty u8 payload")
    return int(payload[0])


def decode_u8_list(payload: bytes) -> list[int]:
    return [int(b) for b in payload]


def decode_u8_tuple5(payload: bytes) -> tuple[int, int, int, int, int]:
    if len(payload) < 5:
        raise ProtocolError(f"Expected 5 bytes, got {payload.hex()}")
    return int(payload[0]), int(payload[1]), int(payload[2]), int(payload[3]), int(payload[4])


def decode_u8_tuple4(payload: bytes) -> tuple[int, int, int, int]:
    if len(payload) < 4:
        raise ProtocolError(f"Expected 4 bytes, got {payload.hex()}")
    return int(payload[0]), int(payload[1]), int(payload[2]), int(payload[3])


def decode_i16_centideg_list(payload: bytes) -> list[float]:
    if len(payload) % 2 != 0:
        raise ProtocolError(f"Expected even byte count, got {payload.hex()}")
    fmt = ">" + "h" * (len(payload) // 2)
    return [x / 100.0 for x in struct.unpack(fmt, payload)]


def decode_preview_ok(payload: bytes) -> bool:
    if len(payload) < 2:
        raise ProtocolError(f"Unexpected M51 payload: {payload.hex()}")
    return payload[0] == 0x00 and payload[1] == 0x01


def decode_pwm_status(payload: bytes) -> list[int]:
    """4 字节：``[激光开关, 激光档位, 自定义开关, 自定义档位]``（各 1 字节）。"""
    if len(payload) < 4:
        raise ProtocolError(f"Expected 4-byte PWM status, got {payload.hex()}")
    return decode_u8_list(payload[:4])


def pack_u16_be(v: int) -> bytes:
    return struct.pack(">H", v & 0xFFFF)


def centi_to_i16(value: float | int, *, strict: bool = True) -> int:
    """物理量 ×100 后编码为 int16（大端有符号字段的数值）。"""
    p = int(round(float(value) * 100.0))
    if strict:
        if p < -32768 or p > 32767:
            raise ValueError(f"value out of int16 range after ×100: {value!r} -> {p}")
        return p
    return struct.unpack(">h", struct.pack(">H", p & 0xFFFF))[0]


def encode_bool_u16(on: bool) -> bytes:
    return bytes([0x00, 0x01 if on else 0x00])


def encode_u8_mask(value: int) -> bytes:
    return bytes([0x00, int(value) & 0xFF])


def encode_u16_level(level: int) -> bytes:
    return bytes([0x00, int(level) & 0xFF])


def encode_joint_index(joint_index: int) -> bytes:
    return bytes([0x00, int(joint_index) & 0xFF])


def encode_gripper_angle(angle: int, speed: int) -> bytes:
    return pack_u16_be(angle) + pack_u16_be(speed)


def kinematics_read_tail(data8: bytes) -> bytes:
    if len(data8) != 8:
        raise ValueError("kinematics tail must be 8 bytes")
    return bytes([0x08]) + data8


def gripper_read_tail(j: int, k: int) -> bytes:
    return bytes([0x04]) + pack_u16_be(j) + pack_u16_be(k)


def float_list_to_centideg_bytes(values: list[float]) -> bytes:
    parts = [int(round(v * 100.0)) for v in values]
    fmt = ">" + "h" * len(parts)
    return struct.pack(fmt, *parts)


def require_payload(data: bytes, length: int, label: str = "payload") -> bytes:
    if len(data) != length:
        raise ValueError(f"{label} must be {length} bytes, got {len(data)}")
    return data


# ---------------------------------------------------------------------------
# 串口事务
# ---------------------------------------------------------------------------


def _install_debug_stream_handler(log: logging.Logger) -> None:
    log.setLevel(logging.DEBUG)
    if log.handlers:
        return
    h = logging.StreamHandler()
    h.setLevel(logging.DEBUG)
    h.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
    log.addHandler(h)
    log.propagate = False


class ModbusRTU:
    """
    P1 Modbus RTU 基类（风格对齐 Pro450 ``ModbusRTU``）。

    - 从站 ``0x2E``，读 ``2E 03 AH AL [tail]``，写 ``2E 10 AH AL BC DATA``
    - 线程锁保护串口事务
    - ``debug=True`` 时 stderr 打印 TX/RX
    """

    def __init__(
        self,
        port: str,
        baudrate: int = 115200,
        timeout: float = 0.3,
        debug: bool = False,
        *,
        validate_limits: bool = True,
        write_timeout: float | None = None,
        event_hook: Callable[[bytes], None] | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.write_timeout = write_timeout if write_timeout is not None else timeout
        self.validate_limits = validate_limits
        self._ser: serial.Serial | None = None
        self._rx = bytearray()
        self._event_hook = event_hook
        self.debug = debug
        self._log = logger if logger is not None else logging.getLogger("p1_modbus.serial")
        self._lock = threading.RLock()
        if debug:
            _install_debug_stream_handler(self._log)

    def _ensure_open(self) -> None:
        if self._ser is not None:
            try:
                if self._ser.is_open:
                    return
            except AttributeError:
                return
        self.open()

    def open(self) -> None:
        with self._lock:
            if self._ser and self._ser.is_open:
                return
            self._ser = serial.Serial(
                self.port,
                self.baudrate,
                timeout=self.timeout,
                write_timeout=self.write_timeout,
            )

    def close(self) -> None:
        with self._lock:
            if self._ser and self._ser.is_open:
                self._ser.close()
            self._ser = None

    def __enter__(self) -> ModbusRTU:
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # noqa: ANN001
        self.close()

    @property
    def serial(self) -> serial.Serial:
        self._ensure_open()
        if not self._ser:
            raise RuntimeError("Serial port failed to open.")
        try:
            if not self._ser.is_open:
                raise RuntimeError("Serial port is not open.")
        except AttributeError:
            pass
        return self._ser

    def poll_events(self, *, max_frames: int = 16) -> list[bytes]:
        """非阻塞读取限位/碰撞主动上报帧。"""
        with self._lock:
            self._ensure_open()
            self._read_into_buffer(allow_block=False)
            out: list[bytes] = []
            for _ in range(max_frames):
                frame = pop_first_frame(self._rx)
                if frame is None:
                    break
                if _is_event_frame(frame):
                    out.append(frame)
                else:
                    self._rx[0:0] = frame
                    break
            return out

    def read_p1(self, addr: int, tail: bytes = b"\x00") -> bytes:
        """P1 读寄存器，返回 DATA 负载（不含地址/CRC）。"""
        pdu = build_read_pdu(addr, tail)
        frame = self.request(pdu, expect_fc=FC_READ)
        return parse_read_payload(frame)

    def write_p1(self, addr: int, data: bytes) -> bytes:
        """P1 写寄存器，返回完整应答帧（含 CRC）。"""
        pdu = build_write_pdu(addr, data)
        return self.request(pdu, expect_fc=FC_WRITE)

    def _read_into_buffer(self, *, allow_block: bool = False) -> None:
        if not self._ser:
            return
        n = self._ser.in_waiting
        if n:
            self._rx.extend(self._ser.read(n))
            return
        if allow_block:
            chunk = self._ser.read(1)
            if chunk:
                self._rx.extend(chunk)

    def request(self, pdu_without_crc: bytes, *, expect_fc: int | None = None) -> bytes:
        """发送不含 CRC 的 PDU，等待首帧非事件应答。"""
        if pdu_without_crc[0] != SLAVE_ID:
            raise ValueError("PDU must start with slave id 0x2E")
        with self._lock:
            self._ensure_open()
            frame_out = append_crc(pdu_without_crc)
            if self.debug:
                self._log.debug("TX %s", frame_out.hex(" ").upper())
            self.serial.write(frame_out)
            self.serial.flush()

            deadline = time.monotonic() + max(self.timeout, 0.05) * 10
            while time.monotonic() < deadline:
                self._read_into_buffer(allow_block=True)
                while True:
                    frame = pop_first_frame(self._rx)
                    if frame is None:
                        break
                    if self.debug:
                        kind = "event" if _is_event_frame(frame) else "frame"
                        self._log.debug("RX (%s) %s", kind, frame.hex(" ").upper())
                    if _is_event_frame(frame):
                        if self._event_hook:
                            self._event_hook(frame)
                        continue
                    if expect_fc is not None and frame[1] != expect_fc:
                        raise ProtocolError(
                            f"Unexpected response function code 0x{frame[1]:02X} "
                            f"(expected 0x{expect_fc:02X}). Frame={frame.hex()}"
                        )
                    return frame
                time.sleep(0.002)
            raise TimeoutError("Timed out waiting for a response frame.")


def _is_event_frame(frame: bytes) -> bool:
    if len(frame) < 8 or frame[0] != SLAVE_ID or frame[1] != FC_WRITE:
        return False
    return frame[2:4] in (b"\x00\x30", b"\x00\x31")
