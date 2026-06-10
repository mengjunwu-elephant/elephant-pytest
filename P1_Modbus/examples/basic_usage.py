"""Example: open port, read firmware version, poll events (edit PORT)."""

from __future__ import annotations

from p1_modbus import P1Client


def main() -> None:
    port = "COM3"  # change for your environment
    with P1Client(port, baudrate=115200, timeout=0.3) as bot:
        ver = bot.read_main_fw_version()
        print(f"Main FW version (G6 u16): {ver}")
        patch = bot.read_main_fw_patch()
        print(f"Main FW patch (G7 u16): {patch}")
        for ev in bot.poll_events():
            print("event:", ev.hex())


if __name__ == "__main__":
    main()
