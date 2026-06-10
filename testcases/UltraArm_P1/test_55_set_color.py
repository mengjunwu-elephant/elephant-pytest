# -*- coding: utf-8 -*-
import time

import allure
import pytest

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import UltraArmP1Base

cases = get_test_data_from_excel(UltraArmP1Base.TEST_DATA_FILE, "set_color")

pytestmark = pytest.mark.peripheral


@allure.feature("设置灯板颜色")
@allure.story("正常用例 - 设置RGB颜色")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_set_color(device, case):
    title = case["title"]
    expected = case["expect_data"]
    r, g, b = case["r"], case["g"], case["b"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'r:{r}')
    logger.debug(f'g:{g}')
    logger.debug(f'b:{b}')

    with allure.step("目测末端RGB灯板颜色变化"):
        input("请确认RGB灯板模块已连接，观察颜色变化，按回车键继续")

    with allure.step(f"调用 {case['api']} 接口"):
        response = device.mc.set_color(r, g, b)
        logger.debug(f"接口返回：{response}")
        time.sleep(2)

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')
