import time
from time import sleep

import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MyAGVProBase

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(MyAGVProBase.TEST_DATA_FILE, "get_auto_report_message")


@allure.feature("读取自动上发内容")
@allure.story("读取自动上发内容（上电）")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "power_on"], ids=lambda c: c["title"])
def test_get_auto_report_message1(device, case):
    title = case["title"]
    expected = eval(case["expect_data"])

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("小车上电"):
        device.mc.power_on()

    with allure.step("调用 set_auto_report_state 接口"):
        response = device.mc.set_auto_report_state(case['parameters'])
        logger.debug(f"设置接口返回：{response}")

    with allure.step("调用 get_auto_report_message 接口"):
        response_get = device.mc.get_auto_report_message()
        logger.debug(f"读取接口返回：{response_get}")

    with allure.step("断言返回值类型为 list"):
        assert isinstance(response_get, list), f"返回类型错误,应为{type(expected)},实际为 {type(response_get)}"

    with allure.step("断言返回值list长度"):
        assert len(response_get) == case['list_len'], f"返回类型错误,应为{type(expected)},实际为 {type(response_get)}"

    with allure.step("断言读取接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response_get), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response_get == expected, f"用例【{title}】断言失败，期望 {expected},实际 {response_get}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("读取自动上发内容")
@allure.story("读取自动上发内容（上电）")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_get_auto_report_message2(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("小车上电"):
        device.mc.power_on()

    with allure.step("调用 set_auto_report_state 接口"):
        response = device.mc.set_auto_report_state(case['parameters'])
        logger.debug(f"设置接口返回：{response}")

    with allure.step("调用 get_auto_report_message 接口"):
        response_get = device.mc.get_auto_report_message()
        logger.debug(f"读取接口返回：{response_get}")

    with allure.step("断言返回值类型"):
        assert response_get is None, f"机械臂返回类型错误，期望None，实际{type(response)}"

    with allure.step("断言读取接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response_get), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response_get == expected, f"用例【{title}】断言失败，期望 {expected},实际 {response_get}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')



@allure.feature("读取自动上发内容")
@allure.story("读取自动上发内容（下电）")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "power_off"], ids=lambda c: c["title"])
def test_get_auto_report_message3(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("小车下电"):
        device.mc.power_off()

    with allure.step("调用 get_auto_report_message 接口"):
        response = device.mc.get_auto_report_message()
        logger.debug(f"接口返回：{response}")

    with allure.step("小车上电"):
        device.mc.power_on()

    with allure.step("断言返回值类型"):
        assert response is None, f"机械臂返回类型错误，期望None，实际{type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')
