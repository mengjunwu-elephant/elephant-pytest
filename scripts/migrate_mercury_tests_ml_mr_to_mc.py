# -*- coding: utf-8 -*-
"""将 testcases 内 device.ml/mr、dev.ml/mr 替换为 .mc，并合并连续重复行。"""
from __future__ import annotations

from pathlib import Path


def migrate_file(path: Path) -> bool:
    raw = path.read_text(encoding="utf-8")
    text = raw
    for old, new in (
        ("device.ml", "device.mc"),
        ("device.mr", "device.mc"),
        ("dev.ml", "dev.mc"),
        ("dev.mr", "dev.mc"),
    ):
        text = text.replace(old, new)
    if text == raw:
        return False
    # 合并连续完全相同的行（去掉双臂重复上电/下电等）
    lines = text.splitlines(keepends=True)
    merged: list[str] = []
    prev: str | None = None
    for line in lines:
        if line == prev:
            continue
        merged.append(line)
        prev = line
    text = "".join(merged)
    path.write_text(text, encoding="utf-8")
    return True


def main() -> None:
    root = Path(__file__).resolve().parent.parent / "testcases"
    n = 0
    for p in sorted(root.rglob("*.py")):
        if migrate_file(p):
            print(p.relative_to(root.parent))
            n += 1
    print("updated files:", n)


if __name__ == "__main__":
    main()
