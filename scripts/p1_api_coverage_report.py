# -*- coding: utf-8 -*-
"""对照 docs/ultraArm_P1_zh.md 与 testcases 目录，输出 API 覆盖报告。"""
from __future__ import annotations

import os
import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DOC = BASE / "docs" / "ultraArm_P1_zh.md"
TEST_DIRS = [
    BASE / "testcases" / "UltraArm_P1",
    BASE / "testcases" / "UltraArm_P1_Attachments",
]

EXCLUDED = {"set_reboot", "get_queue_size", "set_i2c_data"}


def doc_apis() -> list[str]:
    text = DOC.read_text(encoding="utf-8")
    return re.findall(r"### \d+ `(\w+)\(", text)


def tested_apis() -> set[str]:
    found: set[str] = set()
    pat = re.compile(r"device\.mc\.(\w+)\(")
    for d in TEST_DIRS:
        for py in d.glob("test_*.py"):
            found.update(pat.findall(py.read_text(encoding="utf-8", errors="ignore")))
    aliases = {
        "get_screen_modify_version": "get_modify_screen_version",
        "clear_error_information": "clear_error_status",
        "get_base_io_input": "get_base_io_state",
        "get_digital_io_input": "get_end_io_state",
        "is_init_calibration": "get_zero_calibration_state",
        "send_angles": "set_angles",
        "send_coord": "set_coord",
        "send_coords": "set_coords",
    }
    expanded = set(found)
    for k, v in aliases.items():
        if k in found:
            expanded.add(v)
    return expanded


def main() -> int:
    apis = doc_apis()
    tested = tested_apis()
    missing = [a for a in apis if a not in tested and a not in EXCLUDED]
    print(f"文档 API 总数: {len(apis)}")
    print(f"排除: {sorted(EXCLUDED)}")
    print(f"测试已引用 API 数: {len(tested)}")
    print(f"未覆盖 ({len(missing)}):")
    for a in missing:
        print(f"  - {a}")
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
