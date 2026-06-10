# -*- coding: utf-8 -*-
"""UltraArm P1 附件：与主目录一致的串口 device fixture。"""
from __future__ import annotations

import pytest

from common1 import logger
from settings import UltraArmP1Base, resolve_ultraarm_baud, resolve_ultraarm_port


@pytest.fixture(scope="session")
def ultraarm_serial() -> tuple[str, int]:
    port = resolve_ultraarm_port()
    baud = resolve_ultraarm_baud()
    logger.info("ultraarm_serial port=%s baud=%s", port, baud)
    return port, baud


@pytest.fixture(scope="module")
def device(ultraarm_serial: tuple[str, int]) -> UltraArmP1Base:
    port, baud = ultraarm_serial
    dev = UltraArmP1Base(port=port, baud=baud)
    logger.info("初始化完成，附件接口测试开始")
    yield dev
    try:
        dev.mc.set_pwm_laser_mode(0)
    except Exception:
        pass
    dev.mc.close()
    logger.info("环境清理完成，附件接口测试结束")
