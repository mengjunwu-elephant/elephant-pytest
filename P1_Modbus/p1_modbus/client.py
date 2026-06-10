"""Serial client: Modbus RTU framing, CRC, and event demux."""

from __future__ import annotations

import logging
import time
from typing import Callable

import serial

from p1_modbus.crc import append_crc
from p1_modbus.errors import ProtocolError
from p1_modbus.framing import SLAVE_ID, pop_first_frame


def _install_debug_stream_handler(log: logging.Logger) -> None:
    """When ``debug=True``, ensure DEBUG lines reach stderr without user ``basicConfig``."""
    log.setLevel(logging.DEBUG)
    if log.handlers:
        return
    h = logging.StreamHandler()
    h.setLevel(logging.DEBUG)
    h.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
    log.addHandler(h)
    log.propagate = False


class P1ClientBase:
    """
    P1 Modbus RTU client (slave 0x2E).

    The serial port **opens automatically** on first use (``request``, ``poll_events``,
    or the ``serial`` property); you do not need to call :meth:`open` unless you want
    to open early.

    With ``debug=True``, a stderr :class:`logging.StreamHandler` is attached to the
    library logger (if it has no handlers yet) so **TX/RX** hex is visible without
    configuring :mod:`logging` yourself.

    Wire format follows the P1_Modbus protocol sheet: many reads echo the start
    address before ``byte_count``; writes use ``addr_hi addr_lo`` + ``byte_count``
    + ``data`` after ``2E 10``.
    """

    def __init__(
        self,
        port: str,
        baudrate: int = 115200,
        timeout: float = 0.3,
        debug: bool = False,
        *,
        write_timeout: float | None = None,
        event_hook: Callable[[bytes], None] | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.write_timeout = write_timeout if write_timeout is not None else timeout
        self._ser: serial.Serial | None = None
        self._rx = bytearray()
        self._event_hook = event_hook
        self.debug = debug
        self._log = logger if logger is not None else logging.getLogger("p1_modbus.serial")
        if debug:
            self._log.setLevel(logging.DEBUG)
            _install_debug_stream_handler(self._log)

    def _ensure_open(self) -> None:
        """Open the serial port if not already open (used before I/O)."""
        if self._ser is not None:
            try:
                if self._ser.is_open:
                    return
            except AttributeError:
                # Duck-typed port (e.g. tests) without full pyserial API
                return
        self.open()

    def open(self) -> None:
        if self._ser and self._ser.is_open:
            return
        self._ser = serial.Serial(
            self.port,
            self.baudrate,
            timeout=self.timeout,
            write_timeout=self.write_timeout,
        )

    def close(self) -> None:
        if self._ser and self._ser.is_open:
            self._ser.close()
        self._ser = None

    def __enter__(self) -> P1ClientBase:
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
        """
        Non-blocking read of any pending serial data; returns decoded **event** frames.

        Does not perform a request/response transaction. Useful for limit/collision
        auto reports (function codes ``0x10`` sub-address ``0x0030`` / ``0x0031``).
        """
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
        """
        Send one PDU (without CRC), wait for the first non-event response frame.

        ``expect_fc`` optionally asserts the response function code (0x03 or 0x10).
        """
        if pdu_without_crc[0] != SLAVE_ID:
            raise ValueError("PDU must start with slave id 0x2E")
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
    if len(frame) < 8 or frame[0] != SLAVE_ID or frame[1] != 0x10:
        return False
    # ``2E 10 00 30`` / ``2E 10 00 31`` — sub-address 0x0030 / 0x0031
    return frame[2:4] in (b"\x00\x30", b"\x00\x31")
