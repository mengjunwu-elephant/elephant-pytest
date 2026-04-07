# -*- coding: utf-8 -*-
"""pytest 共享 fixture：机械臂 IP（环境变量）与模块级 device 连接。"""
from __future__ import annotations

import pytest

from common1 import logger
from settings import MyAGVProBase




@pytest.fixture(scope="module")
def device(mycobot_ip: str) -> MyAGVProBase:
    """模块级单连接；teardown 仅关闭 socket。

    若某测试模块需要自定义清理（恢复参数、夹爪等），可在该模块内重新定义同名
    `device` fixture，将覆盖此处定义（pytest 就近覆盖规则）。
    """
    dev = MyAGVProBase(ip=mycobot_ip)
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.close()
    logger.info("环境清理完成，接口测试结束")


