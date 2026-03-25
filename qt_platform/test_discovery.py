# -*- coding: utf-8 -*-
"""扫描 test_*.py，解析接口表名与各 test 函数；优先用 @allure.story 作为测试项展示名。"""
from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path

_SHEET_RE = re.compile(
    r'get_test_data_from_excel\s*\(\s*[^,]+,\s*["\']([^"\']+)["\']',
    re.MULTILINE,
)
# 文件名 test_12_xxx.py 按数字 12 排序，避免字符串顺序下 test_10 排在 test_2 前
_TEST_FILE_NUM = re.compile(r"test_(\d+)_", re.IGNORECASE)


@dataclass(frozen=True)
class TestItem:
    """单个可运行测试项：对应一个 test_* 函数。"""

    func_name: str
    label: str  # 界面展示（通常来自 @allure.story）
    uses_input: bool = False  # 函数体内是否调用 input()（需人工交互）


@dataclass
class TestModuleRow:
    """单行：一个测试文件，内含若干测试项（按源码顺序）。"""

    rel_path: str  # posix 相对项目根
    display_name: str  # 表名或推导名
    items: list[TestItem] = field(default_factory=list)

    def choice_uses_input(self, choice: str) -> bool:
        """当前选择的测试项是否包含 input()（含「全部」时任一函数含即 True）。"""
        if choice == "__ALL__":
            return any(i.uses_input for i in self.items)
        for i in self.items:
            if i.func_name == choice:
                return i.uses_input
        return False

    def pytest_k_expr_for(self, choice: str) -> str | None:
        """
        choice: 某 TestItem.func_name，或 "__ALL__" 表示本文件全部 test 函数。
        返回传给 pytest -k 的表达式。
        """
        names = [i.func_name for i in self.items]
        if not names:
            return None
        if choice == "__ALL__":
            return names[0] if len(names) == 1 else " or ".join(names)
        if choice in names:
            return choice
        return None


def _string_from_ast_constant(node: ast.expr) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    str_node = getattr(ast, "Str", None)
    if str_node is not None and isinstance(node, str_node):
        return getattr(node, "s", None)
    return None


def _allure_story_label(decorator_list: list[ast.expr]) -> str | None:
    """匹配 @allure.story("标题")。"""
    for dec in decorator_list:
        if not isinstance(dec, ast.Call):
            continue
        func = dec.func
        if not isinstance(func, ast.Attribute) or func.attr != "story":
            continue
        if not isinstance(func.value, ast.Name):
            continue
        if func.value.id != "allure":
            continue
        if not dec.args:
            continue
        s = _string_from_ast_constant(dec.args[0])
        if s is not None:
            return s.strip() or None
    return None


def _function_body_uses_input(node: ast.FunctionDef) -> bool:
    """检测 test 函数体内是否调用 input(...)。"""
    for n in ast.walk(node):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "input":
            return True
    return False


def _label_for_test_function(name: str, story: str | None, used_base: dict[str, int]) -> str:
    base = (story or "").strip() or name
    n = used_base.get(base, 0)
    used_base[base] = n + 1
    if n == 0:
        return base
    return f"{base} ({name})"


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
        used: dict[str, int] = {}
        items: list[TestItem] = []
        for node in tree.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            if not node.name.startswith("test_"):
                continue
            story = _allure_story_label(node.decorator_list)
            label = _label_for_test_function(node.name, story, used)
            uses_in = _function_body_uses_input(node)
            items.append(
                TestItem(func_name=node.name, label=label, uses_input=uses_in),
            )
        if not items:
            continue
        rel = p.relative_to(project_root).as_posix()
        rows.append(
            TestModuleRow(rel_path=rel, display_name=display, items=items),
        )
    rows.sort(key=lambda r: _pytest_file_sort_key(r.rel_path))
    return rows


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
