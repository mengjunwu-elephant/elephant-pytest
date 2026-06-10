# -*- coding: utf-8 -*-
import time

import allure
import pytest

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import UltraArmP1Base

cases = get_test_data_from_excel(UltraArmP1Base.ATTACHMENTS_TEST_DATA_FILE, "open_laser")

pytestmark = pytest.mark.peripheral


@allure.feature("设置激光打开")
@allure.story("正确激光打开")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_open_laser(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("提示请连接激光雕刻模块"):
        input("请确认机械臂已连接激光雕刻模块，激光会持续5s，按回车键继续")

    with allure.step(f'调用 {case["api"]} 接口'):
        response = device.mc.set_pwm_laser_mode(1)
        logger.debug(f"接口返回：{response}")
        time.sleep(5)

    with allure.step("调用 set_pwm_laser_mode(0) 关闭激光"):
        device.mc.set_pwm_laser_mode(0)

    with allure.step("确认激光已打开，且5s后关闭"):
        res = input("请确认激光是否打开5s后关闭，输入0测试失败，按回车键继续")
        if res == "0":
            pytest.fail("激光未生效")

    with allure.step("断言返回值"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert str(response).lower() in ("ok", "1", str(expected).lower()), (
            f"用例【{title}】断言失败，期望 {expected},实际 {response}"
        )

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')
