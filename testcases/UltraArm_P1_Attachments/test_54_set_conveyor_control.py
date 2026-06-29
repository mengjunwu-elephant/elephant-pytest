# -*- coding: utf-8 -*-
import time

import allure
import pytest

from common1 import logger
from common1.operator_input import prompt_continue
from common1.test_data_handler import get_test_data_from_excel
from settings import UltraArmP1Base

cases = get_test_data_from_excel(UltraArmP1Base.TEST_DATA_FILE, "set_conveyor_control")

@allure.feature("传送带控制")
@allure.story("正常用例 - 传送带控制")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_set_conveyor_control(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'state:{case["state"]}')
    logger.debug(f'direction:{case["direction"]}')
    logger.debug(f'speed:{case["speed"]}')
    logger.debug(f'distance:{case["distance"]}')

    with allure.step("确认传送带模块已连接"):
        prompt_continue("请确认传送带模块已连接，按回车键继续")

    with allure.step(f"调用 {case['api']} 接口"):
        response = device.mc.set_conveyor_control(
            case["state"],
            case["direction"],
            case["speed"],
            case["distance"],
        )
        logger.debug(f"接口返回：{response}")
        time.sleep(2)

    with allure.step("断言返回值类型为 str"):
        assert isinstance(response, str), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')
