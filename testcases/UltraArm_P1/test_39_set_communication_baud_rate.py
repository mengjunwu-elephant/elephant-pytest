# -*- coding: utf-8 -*-
import os

import pytest
import allure
from pymycobot.error import ultraArmP1DataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import UltraArmP1Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(UltraArmP1Base.TEST_DATA_FILE, "set_communication_baud_rate")

pytestmark = [
    pytest.mark.firmware,
    pytest.mark.skipif(
        not os.environ.get("RUN_P1_FIRMWARE"),
        reason="需要设置 RUN_P1_FIRMWARE=1 才运行固件/波特率相关用例",
    ),
]


@allure.feature("通信波特率")
@allure.story("超限参数验证")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_communication_baud_rate_exception(device, case):
    title = case["title"]
    baud_rate = case["baud_rate"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'baud_rate:{baud_rate}')

    with allure.step(f"断言抛出 ultraArmP1DataException，波特率为 {baud_rate}"):
        with pytest.raises(ultraArmP1DataException) as exc:
            device.mc.set_communication_baud_rate(baud_rate)

    logger.info(f"✅ 用例【{title}】异常断言通过,异常信息：{exc.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")
