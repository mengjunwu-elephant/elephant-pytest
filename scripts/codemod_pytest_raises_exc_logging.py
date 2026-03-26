#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量：pytest.raises 补 as exc、exc_info 统一为 exc、异常通过类 logger 补 exc.value。"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "testcases"


def patch_file(text: str) -> str:
    text = re.sub(r"\)as exc_info:", ") as exc_info:", text)
    text = text.replace(") as exc_info:", ") as exc:")
    text = text.replace("exc_info.value", "exc.value")

    lines = text.splitlines(keepends=True)
    out: list[str] = []
    for line in lines:
        raw = line
        s = line.rstrip("\r\n")
        trail = line[len(s) :]
        if (
            "with pytest.raises" in s
            and s.rstrip().endswith("):")
            and " as exc" not in s
        ):
            t = s.rstrip()
            if t.endswith("):"):
                t = t[:-2] + ") as exc:"
                s = t
        out.append(s + trail)
    text = "".join(out)
    while ") as exc as exc:" in text:
        text = text.replace(") as exc as exc:", ") as exc:")

    def fix_exc_logger_line(stripped: str) -> str | None:
        if "logger.info(f" not in stripped or "✅" not in stripped:
            return None
        if "异常信息" in stripped or "触发了预期异常" in stripped:
            return None
        if not any(
            k in stripped
            for k in ("异常断言通过", "异常断言成功", "异常测试通过")
        ):
            return None
        if stripped.endswith('")'):
            return stripped[:-2] + ',异常信息：{exc.value}")'
        if stripped.endswith("')"):
            return stripped[:-2] + ",异常信息：{exc.value}')"
        return None

    lines = text.splitlines(keepends=True)
    out2: list[str] = []
    for line in lines:
        s = line.rstrip("\r\n")
        trail = line[len(s) :]
        ns = fix_exc_logger_line(s)
        out2.append((ns if ns is not None else s) + trail)
    return "".join(out2)


def main() -> None:
    changed = 0
    for path in sorted(ROOT.rglob("*.py")):
        old = path.read_text(encoding="utf-8")
        new = patch_file(old)
        if new != old:
            path.write_text(new, encoding="utf-8")
            changed += 1
            print("updated", path.relative_to(ROOT.parent))
    print("files changed:", changed)


if __name__ == "__main__":
    main()
