# -*- coding: utf-8 -*-
import pytest
import allure

from common1 import logger
from common1.operator_input import prompt_continue
from common1.test_data_handler import get_test_data_from_excel
from settings import UltraArmP1Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(UltraArmP1Base.TEST_DATA_FILE, "get_bluetooth_mac")

@allure.feature("获取蓝牙MAC")
@allure.story("蓝牙开启状态下获取MAC地址")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_get_bluetooth_mac(device, case):
    title = case["title"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("确认蓝牙已开启"):
        prompt_continue("请确认机械臂蓝牙已开启，按回车键继续测试")

    with allure.step(f"调用 {case['api']} 接口"):
        response = device.mc.get_bluetooth_mac()
        logger.debug(f"接口返回：{response}")

    with allure.step("断言返回值类型为 str"):
        assert isinstance(response, str), f"返回类型错误，应为 str，实际为 {type(response)}"

    with allure.step("断言接口返回非空"):
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response, f"用例【{title}】断言失败，蓝牙 MAC 不应为空"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')
