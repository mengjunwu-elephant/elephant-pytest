# -*- coding: utf-8 -*-
import os

import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import UltraArmP1Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(UltraArmP1Base.TEST_DATA_FILE, "upgrade_restart")

pytestmark = [
    pytest.mark.firmware,
    pytest.mark.skipif(
        not os.environ.get("RUN_P1_FIRMWARE"),
        reason="需要设置 RUN_P1_FIRMWARE=1 才运行固件相关用例",
    ),
]


@allure.feature("固件升级")
@allure.story("固件升级重启")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") in ("normal", "skip")], ids=lambda c: c["title"])
def test_upgrade_restart(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step(f"调用 {case['api']} 接口"):
        response = device.mc.upgrade_restart()
        logger.debug(f"接口返回：{response}")

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        if expected is not None:
            assert response == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')
