# -*- coding: utf-8 -*-
"""pytest 共享 fixture：Mercury A1 串口参数（环境变量）与模块级 device。"""
from __future__ import annotations

import pytest

from common1 import logger
from settings import MercuryBase, resolve_mercury_left_port


@pytest.fixture(scope="session")
def mercury_left_port() -> str:
    """当前会话使用的左臂串口（日志与排查）。"""
    port = resolve_mercury_left_port()
    logger.info("mercury_left_port=%s", port)
    return port


@pytest.fixture(scope="module")
def device(mercury_left_port: str) -> MercuryBase:
    """模块级连接；teardown 仅 close。

    各用例文件若自定义上电/回零/双通道逻辑，可在模块内重新定义同名 `device` fixture
    覆盖本定义（pytest 就近覆盖规则）。
    """
    dev = MercuryBase(left_port=mercury_left_port)
    logger.info("初始化完成（conftest 默认 device，未自动上电）")
    yield dev
    dev.close()
    logger.info("环境清理完成，连接已关闭")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """为 testcases 下用例自动打 hardware，便于 CI：pytest -m \"not hardware\"。"""
    for item in items:
        fspath = str(getattr(item, "fspath", "") or getattr(item, "path", ""))
        if "testcases" not in fspath.replace("\\", "/"):
            continue
        if any(m.name == "hardware" for m in item.iter_markers()):
            continue
        item.add_marker(pytest.mark.hardware)
