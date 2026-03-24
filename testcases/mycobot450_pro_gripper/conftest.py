# -*- coding: utf-8 -*-
"""Pro 450 夹爪用例：与 mycobot_450 共用 Pro450Client 连接逻辑。"""
from __future__ import annotations

from typing import Any

import pytest

from arm_registry import build_device, resolve_arm_id, resolve_device_ip
from common1 import logger


@pytest.fixture(scope="session")
def elephant_arm_id(request: pytest.FixtureRequest) -> str:
    return resolve_arm_id(request.config.getoption("--elephant-arm"))


@pytest.fixture(scope="session")
def mycobot_ip(request: pytest.FixtureRequest, elephant_arm_id: str) -> str:
    ip = resolve_device_ip("mycobot450", request.config.getoption("--elephant-ip"))
    logger.info("session_arm=%s mycobot450_ip=%s", elephant_arm_id, ip)
    return ip


@pytest.fixture(scope="module")
def device(mycobot_ip: str) -> Any:
    dev = build_device("mycobot450", mycobot_ip)
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.close()
    logger.info("环境清理完成，接口测试结束")
