# -*- coding: utf-8 -*-
"""pytest 共享 fixture：机械臂 IP（环境变量）与模块级 device 连接。"""
from __future__ import annotations

import pytest

from common1 import logger
from settings import Mycobot450Base, resolve_mycobot450_ip


@pytest.fixture(scope="session")
def mycobot_ip() -> str:
    """控制器 IP：环境变量 MYCOBOT450_IP 或 Mycobot450_IP，否则使用 settings 默认。"""
    ip = resolve_mycobot450_ip()
    logger.info("mycobot_ip=%s", ip)
    return ip


@pytest.fixture(scope="module")
def device(mycobot_ip: str) -> Mycobot450Base:
    """模块级单连接；teardown 仅关闭 socket。

    若某测试模块需要自定义清理（恢复参数、夹爪等），可在该模块内重新定义同名
    `device` fixture，将覆盖此处定义（pytest 就近覆盖规则）。
    """
    dev = Mycobot450Base(ip=mycobot_ip)
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
