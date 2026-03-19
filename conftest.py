# -*- coding: utf-8 -*-
"""全局 pytest 配置与共享 fixture，避免各用例重复定义 device。"""
import pytest

from common1 import logger
from settings import UltraArmP1Base


@pytest.fixture(scope="module")
def device():
    """设备初始化和清理（串口/波特率由 settings 读取，支持环境变量 ULTRAARM_PORT / ULTRAARM_BAUD）。"""
    dev = UltraArmP1Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.close()
    logger.info("环境清理完成，接口测试结束")
