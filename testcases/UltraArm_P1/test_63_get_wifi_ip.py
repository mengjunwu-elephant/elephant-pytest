# -*- coding: utf-8 -*-
import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import UltraArmP1Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(UltraArmP1Base.TEST_DATA_FILE, "get_wifi_ip")

pytestmark = pytest.mark.peripheral


@allure.feature("获取WiFi IP")
@allure.story("WiFi连接状态下获取IP地址")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_get_wifi_ip(device, case):
    title = case["title"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("确认 WiFi 已连接"):
        input("请确认机械臂 WiFi 已连接，按回车键继续测试")

    with allure.step(f"调用 {case['api']} 接口"):
        response = device.mc.get_wifi_ip()
        logger.debug(f"接口返回：{response}")

    with allure.step("断言返回值类型为 str"):
        assert isinstance(response, str), f"返回类型错误，应为 str，实际为 {type(response)}"

    with allure.step("断言接口返回非空"):
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response, f"用例【{title}】断言失败，WiFi IP 不应为空"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')
