# -*- coding: utf-8 -*-
"""pytest 共享 fixture：串口参数（环境变量）与模块级 device。"""
from __future__ import annotations

import pytest

from common1 import logger
from settings import (
    UltraArmP1Base,
    resolve_ultraarm_baud,
    resolve_ultraarm_port,
)


@pytest.fixture(scope="session")
def ultraarm_serial() -> tuple[str, int]:
    """当前用例使用的串口与波特率（便于日志与排查）。"""
    port = resolve_ultraarm_port()
    baud = resolve_ultraarm_baud()
    logger.info("ultraarm_serial port=%s baud=%s", port, baud)
    return port, baud


@pytest.fixture(scope="module")
def device(ultraarm_serial: tuple[str, int]) -> UltraArmP1Base:
    """模块级单连接；teardown 仅关闭串口。

    若某测试模块需要自定义清理（回零、夹爪、IO 复位等），可在该模块内重新定义同名
    `device` fixture，将覆盖此处定义（pytest 就近覆盖规则）。
    """
    port, baud = ultraarm_serial
    dev = UltraArmP1Base(port=port, baud=baud)
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.close()
    logger.info("环境清理完成，接口测试结束")


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """为 testcases 下收集到的用例自动打上 hardware，便于 CI：pytest -m \"not hardware\"。"""
    for item in items:
        fspath = str(getattr(item, "fspath", "") or getattr(item, "path", ""))
        if "testcases" not in fspath.replace("\\", "/"):
            continue
        if any(m.name == "hardware" for m in item.iter_markers()):
            continue
        item.add_marker(pytest.mark.hardware)
