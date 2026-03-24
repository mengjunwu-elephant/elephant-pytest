# -*- coding: utf-8 -*-
"""扫描 test_*.py，解析 Excel sheet 名与 test 函数，按名称粗分 normal / exception。"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

_SHEET_RE = re.compile(
    r'get_test_data_from_excel\s*\(\s*[^,]+,\s*["\']([^"\']+)["\']',
    re.MULTILINE,
)
# 文件名 test_12_xxx.py 按数字 12 排序，避免字符串顺序下 test_10 排在 test_2 前
_TEST_FILE_NUM = re.compile(r"test_(\d+)_", re.IGNORECASE)


@dataclass
class TestModuleRow:
    """单行：一个测试文件对应一个接口/表名。"""

    rel_path: str  # posix 相对项目根
    display_name: str  # 表名或推导名
    normal_funcs: list[str] = field(default_factory=list)
    exception_funcs: list[str] = field(default_factory=list)

    def pytest_k_for(self, kind: Literal["normal", "exception"]) -> str | None:
        names = self.normal_funcs if kind == "normal" else self.exception_funcs
        if not names:
            return None
        if len(names) == 1:
            return names[0]
        return " or ".join(names)

    def has_kind(self, kind: Literal["normal", "exception"]) -> bool:
        return bool(self.normal_funcs if kind == "normal" else self.exception_funcs)


def _classify_function(name: str) -> Literal["normal", "exception"]:
    n = name.lower()
    if "exception" in n or "emergency" in n:
        return "exception"
    return "normal"


def _sheet_from_stem(stem: str) -> str:
    # test_1_get_system_version -> get_system_version
    if stem.startswith("test_"):
        rest = stem[5:]
        parts = rest.split("_", 1)
        if len(parts) == 2 and parts[0].isdigit():
            return parts[1]
        return rest
    return stem


def _pytest_file_sort_key(rel_posix: str) -> tuple[int, int, str]:
    """同一目录内：优先按 test_<数字>_ 中的数字升序，其余按文件名。"""
    name = Path(rel_posix).name
    m = _TEST_FILE_NUM.search(name)
    if m:
        return (0, int(m.group(1)), name.lower())
    return (1, 0, name.lower())


def discover_under_root(project_root: Path, testcase_root: str) -> list[TestModuleRow]:
    project_root = project_root.resolve()
    root = (project_root / testcase_root).resolve()
    if not root.is_dir():
        return []
    rows: list[TestModuleRow] = []
    for p in sorted(root.glob("test_*.py")):
        if p.name == "conftest.py":
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except OSError:
            continue
        m = _SHEET_RE.search(text)
        display = m.group(1) if m else _sheet_from_stem(p.stem)
        try:
            tree = ast.parse(text, filename=str(p))
        except SyntaxError:
            continue
        normal: list[str] = []
        exc: list[str] = []
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                cat = _classify_function(node.name)
                (exc if cat == "exception" else normal).append(node.name)
        if not normal and not exc:
            continue
        rel = p.relative_to(project_root).as_posix()
        rows.append(
            TestModuleRow(
                rel_path=rel,
                display_name=display,
                normal_funcs=sorted(normal),
                exception_funcs=sorted(exc),
            )
        )
    rows.sort(key=lambda r: _pytest_file_sort_key(r.rel_path))
    return rows


def discover_for_arm(project_root: Path, testcase_roots: list[str]) -> list[TestModuleRow]:
    """扁平列表（跨根去重），顺序为 arms 中 testcase_roots 顺序 + 组内数字序。"""
    seen: set[str] = set()
    out: list[TestModuleRow] = []
    for tr in testcase_roots:
        for row in discover_under_root(project_root, tr):
            if row.rel_path in seen:
                continue
            seen.add(row.rel_path)
            out.append(row)
    return out


def discover_grouped_for_arm(
    project_root: Path, testcase_roots: list[str]
) -> list[tuple[str, list[TestModuleRow]]]:
    """按 arms.json 中每个 testcase_root 一组；组内已按 test_ 后数字排序；跨组去重路径。"""
    seen: set[str] = set()
    groups: list[tuple[str, list[TestModuleRow]]] = []
    for tr in testcase_roots:
        chunk: list[TestModuleRow] = []
        for row in discover_under_root(project_root, tr):
            if row.rel_path in seen:
                continue
            seen.add(row.rel_path)
            chunk.append(row)
        if chunk:
            groups.append((tr, chunk))
    return groups
