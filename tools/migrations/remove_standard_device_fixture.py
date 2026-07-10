# -*- coding: utf-8 -*-
"""一次性工具：从测试模块中删除与根 conftest 完全一致的标准 device fixture。"""
from __future__ import annotations

from pathlib import Path

STANDARD_NO_DOC = [
    "dev = Mycobot450Base()",
    'logger.info("初始化完成，接口测试开始")',
    "yield dev",
    "dev.mc.close()",
    'logger.info("环境清理完成，接口测试结束")',
]
STANDARD_WITH_DOC = ['"""设备初始化和清理"""'] + STANDARD_NO_DOC


def _fixture_body_lines(raw_lines: list[str]) -> list[str]:
    """去掉 fixture 体左侧 4 空格，去掉首尾空行。"""
    out = [ln[4:] if ln.startswith("    ") else ln for ln in raw_lines]
    while out and out[0].strip() == "":
        out.pop(0)
    while out and out[-1].strip() == "":
        out.pop()
    return out


def _find_device_fixture_span(lines: list[str]) -> tuple[int, int] | None:
    for i in range(len(lines) - 1):
        if lines[i].strip() != '@pytest.fixture(scope="module")':
            continue
        if "def device():" not in lines[i + 1]:
            continue
        start = i
        j = i + 2
        while j < len(lines):
            line = lines[j]
            if line.strip() == "":
                j += 1
                continue
            if line.startswith("    ") or line.startswith("\t"):
                j += 1
                continue
            break
        return start, j
    return None


def try_strip(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    newline = "\r\n" if "\r\n" in text else "\n"
    lines = text.splitlines()
    span = _find_device_fixture_span(lines)
    if span is None:
        return False
    start, end = span
    body = _fixture_body_lines(lines[start + 2 : end])
    stripped = [ln.rstrip() for ln in body if ln.strip() != ""]
    if stripped == STANDARD_NO_DOC or stripped == STANDARD_WITH_DOC:
        del lines[start:end]
        # 去掉 fixture 后多余空行（最多保留一个）
        if start < len(lines) and start > 0:
            if lines[start].strip() == "" and lines[start - 1].strip() == "":
                del lines[start]
        new_text = newline.join(lines)
        if not new_text.endswith(newline):
            new_text += newline
        path.write_text(new_text, encoding="utf-8")
        return True
    return False


def main() -> None:
    root = Path(__file__).resolve().parent.parent / "testcases"
    n = 0
    for p in sorted(root.rglob("test_*.py")):
        if try_strip(p):
            print("stripped", p.relative_to(root.parent))
            n += 1
    print("total stripped:", n)


if __name__ == "__main__":
    main()
