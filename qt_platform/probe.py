# -*- coding: utf-8 -*-
"""子进程探测连接：python -m qt_platform.probe <arm_id> ..."""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]


def _close_device(dev: object) -> None:
    try:
        if hasattr(dev, "mc") and dev.mc is not None:
            close = getattr(dev.mc, "close", None)
            if callable(close):
                close()
        elif hasattr(dev, "close") and callable(dev.close):
            dev.close()
    except Exception as e:  # noqa: BLE001
        print(f"WARN close: {e}", file=sys.stderr)


def run_probe(arm_id: str, ip: str | None, serial: str | None, left: str | None, right: str | None) -> int:
    os.chdir(_ROOT)
    if str(_ROOT) not in sys.path:
        sys.path.insert(0, str(_ROOT))

    from arm_registry import build_device, get_connection_mode

    mode = get_connection_mode(arm_id)
    dev = None
    try:
        if mode == "ip":
            if not (ip or "").strip():
                print("缺少 IP", file=sys.stderr)
                return 2
            dev = build_device(arm_id, ip.strip())
            mc = getattr(dev, "mc", None)
            if mc is not None and hasattr(mc, "get_system_version"):
                v = mc.get_system_version()
                print(f"OK get_system_version={v!r}")
            else:
                print("OK 已连接（无 get_system_version）")
        elif mode == "serial":
            if not (serial or "").strip():
                print("缺少串口", file=sys.stderr)
                return 2
            dev = build_device(arm_id, serial.strip())
            mc = getattr(dev, "mc", None)
            if mc is not None and hasattr(mc, "get_system_version"):
                v = mc.get_system_version()
                print(f"OK get_system_version={v!r}")
            else:
                print("OK 已连接")
        elif mode == "dual_serial":
            if not (left or "").strip() or not (right or "").strip():
                print("缺少左右臂串口", file=sys.stderr)
                return 2
            os.environ["MERCURY_LEFT_PORT"] = left.strip()
            os.environ["MERCURY_RIGHT_PORT"] = right.strip()
            dev = build_device(arm_id, "")
            ml = getattr(dev, "ml", None)
            if ml is not None and hasattr(ml, "get_system_version"):
                v = ml.get_system_version()
                print(f"OK 左臂 get_system_version={v!r}")
            else:
                print("OK 双臂对象已创建")
        else:
            print(f"未知 connection_mode: {mode}", file=sys.stderr)
            return 2
        return 0
    except Exception as e:  # noqa: BLE001
        print(f"FAIL {e!r}", file=sys.stderr)
        return 1
    finally:
        if dev is not None:
            _close_device(dev)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("arm_id")
    p.add_argument("--ip", default=None)
    p.add_argument("--serial", default=None)
    p.add_argument("--left", default=None)
    p.add_argument("--right", default=None)
    args = p.parse_args()
    sys.exit(
        run_probe(
            args.arm_id,
            args.ip,
            args.serial,
            args.left,
            args.right,
        )
    )


if __name__ == "__main__":
    main()
