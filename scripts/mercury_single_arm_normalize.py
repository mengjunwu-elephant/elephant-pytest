# -*- coding: utf-8 -*-
"""
Mercury A1 单臂：去掉右臂重复调用/断言，文案左/右臂 -> 机械臂；
删除 test_*_right，将 test_*_left 重命名为 test_*。
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "testcases" / "mercury"


def extract_mc_rhs(line: str) -> str | None:
    m = re.search(r"=\s*(device\.mc\..*)", line)
    return m.group(1).strip() if m else None


def is_l_assign(line: str) -> bool:
    return bool(re.match(r"\s*l_(response|move|res|curr|get_res)\s*=", line))


def is_r_assign(line: str) -> bool:
    return bool(re.match(r"\s*r_(response|move|res|curr|get_res)\s*=", line))


def dedupe_lr_pairs(text: str) -> str:
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if i + 1 < len(lines) and is_l_assign(line) and is_r_assign(lines[i + 1]):
            a, b = extract_mc_rhs(line), extract_mc_rhs(lines[i + 1])
            if a and b and a == b:
                nl = (
                    line.replace("l_response", "response")
                    .replace("l_move", "move_res")
                    .replace("l_res", "res")
                    .replace("l_curr", "curr")
                    .replace("l_get_res", "get_res")
                )
                out.append(nl)
                i += 2
                continue
        out.append(line)
        i += 1
    return "".join(out)


def remove_lines_with_r_vars(text: str) -> str:
    """删除仍引用 r_response / r_expect 等的整行（含 allure.attach / assert / logger）。"""
    kill_prefixes = (
        "r_response",
        "r_move",
        "r_res",
        "r_curr",
        "r_get_res",
        "expected_r",
        "case[\"r_expect_data\"]",
        "case['r_expect_data']",
    )
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    for line in lines:
        stripped = line.lstrip()
        if any(k in line for k in kill_prefixes):
            # 保留可能在字符串里误伤——极少；异常场景双臂各测一次时删右臂 step
            if re.search(
                r"\b(r_response|r_move|r_res|r_curr|r_get_res|expected_r)\b", line
            ):
                continue
            if "r_expect_data" in line:
                continue
        out.append(line)
    return "".join(out)


def rename_l_vars_to_neutral(text: str) -> str:
    return (
        text.replace("l_response", "response")
        .replace("l_move", "move_res")
        .replace("l_res", "res")
        .replace("l_curr", "curr")
        .replace("l_get_res", "get_res")
        .replace("expected_l", "expected")
    )


def chinese_arm_names(text: str) -> str:
    text = text.replace("左右臂", "机械臂")
    text = text.replace("左臂", "机械臂")
    text = text.replace("右臂", "机械臂")
    return text


def remove_test_right_functions(text: str) -> str:
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^(\s*)def (test_\w+_right)\s*\(", line)
        if m:
            base_indent = len(m.group(1))
            i += 1
            while i < len(lines):
                ln = lines[i]
                if not ln.strip():
                    i += 1
                    continue
                ind = len(ln) - len(ln.lstrip())
                if ind <= base_indent and (
                    ln.lstrip().startswith("def ")
                    or ln.lstrip().startswith("@")
                ):
                    break
                i += 1
            continue
        out.append(line)
        i += 1
    return "".join(out)


def rename_test_left_functions(text: str) -> str:
    return re.sub(
        r"\bdef (test_\w+)_left\s*\(",
        r"def \1(",
        text,
    )


def collapse_empty_allure_steps(text: str) -> str:
    """删除空的 with allure.step(...): 块（仅含空白）。"""
    pattern = re.compile(
        r"^\s*with allure\.step\([^)]+\):\s*\n\s*\n",
        re.MULTILINE,
    )
    prev = None
    while prev != text:
        prev = text
        text = pattern.sub("", text)
    return text


def process_file(path: Path) -> bool:
    raw = path.read_text(encoding="utf-8")
    text = raw
    text = remove_test_right_functions(text)
    text = rename_test_left_functions(text)
    text = dedupe_lr_pairs(text)
    text = remove_lines_with_r_vars(text)
    text = rename_l_vars_to_neutral(text)
    text = chinese_arm_names(text)
    text = collapse_empty_allure_steps(text)
    if text != raw:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    n = 0
    for p in sorted(ROOT.glob("test_*.py")):
        if process_file(p):
            print(p.name)
            n += 1
    print("updated:", n)


if __name__ == "__main__":
    main()
