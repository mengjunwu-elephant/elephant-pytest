# -*- coding: utf-8 -*-
"""根 conftest：仅注册 CLI 与用例标记；各产品线 device 在对应 testcases 子目录下定义。"""
from __future__ import annotations

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    parser.addoption(
        "--elephant-arm",
        action="store",
        default=None,
        help="机械臂 ID（arms.json），亦可设环境变量 ELEPHANT_ARM",
    )
    parser.addoption(
        "--elephant-ip",
        action="store",
        default=None,
        help="Pro450 控制器 IP；优先于环境变量与 arms.json default_ip",
    )


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    for item in items:
        fspath = str(getattr(item, "fspath", "") or getattr(item, "path", ""))
        if "testcases" not in fspath.replace("\\", "/"):
            continue
        if any(m.name == "hardware" for m in item.iter_markers()):
            continue
        item.add_marker(pytest.mark.hardware)
