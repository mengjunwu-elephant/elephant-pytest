#!/usr/bin/env python3
"""Probe candidate Modbus addresses for M39/M46/M47/M84 (debug TX/RX)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# 允许在未 pip install 时从 P1_Modbus 目录直接运行：
#   python scripts/probe_missing_modbus.py COM5
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from p1_modbus import UltraArmP1Modbus  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe unverified P1 Modbus registers")
    parser.add_argument("port", help="Serial port, e.g. COM5")
    parser.add_argument("--baudrate", type=int, default=115200)
    args = parser.parse_args()

    with UltraArmP1Modbus(args.port, baudrate=args.baudrate, timeout=0.5, debug=True) as arm:
        print("M39 set_conveyor_stop ...")
        try:
            arm.set_conveyor_stop()
            print("  OK")
        except Exception as exc:
            print(f"  FAIL: {exc}")

        print("get_pwm_status ...")
        try:
            print(" ", arm.get_pwm_status())
        except Exception as exc:
            print(f"  FAIL: {exc}")

        print("coord_inverse_solution [170,0,41,0] ...")
        try:
            print(" ", arm.coord_inverse_solution([170.0, 0.0, 41.0, 0.0]))
        except Exception as exc:
            print(f"  FAIL: {exc}")

        print("angle_correct_solution [0,20,110,0] ...")
        try:
            print(" ", arm.angle_correct_solution([0.0, 20.0, 110.0, 0.0]))
        except Exception as exc:
            print(f"  FAIL: {exc}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
