import time
from time import sleep

import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MyAGVProBase

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(MyAGVProBase.TEST_DATA_FILE, "set_communication_state")


@allure.feature("设置通信模式")
@allure.story("设置通信模式（上电）")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "power_on"], ids=lambda c: c["title"])
def test_set_communication_state1(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("小车上电"):
        device.mc.power_on()

    with allure.step("调用 set_communication_state 接口"):
        response = device.mc.set_communication_state(case['state'])
        logger.debug(f"设置接口返回：{response}")

    with allure.step("调用 get_communication_state 接口"):
        response_get = device.mc.get_communication_state()
        logger.debug(f"读取接口返回：{response_get}")

    if case['state'] == 2:
        input(f'请按下松开急停后, 回车继续测试')

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言设置接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    with allure.step("断言读取接口返回结果"):
        allure.attach(str(case['expect_data_get']), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response_get), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response_get == case['expect_data_get'], f"用例【{title}】断言失败，期望 {case['expect_data_get']},实际 {response_get}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')


@allure.feature("设置通信模式")
@allure.story("设置通信模式（下电）")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "power_off"], ids=lambda c: c["title"])
def test_set_communication_state2(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("小车下电"):
        device.mc.power_off()

    with allure.step("调用 set_communication_state 接口"):
        response = device.mc.set_communication_state(case['state'])
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

@allure.feature("设置通信模式")
@allure.story("设置通信模式（参数超限）")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_communication_state3(device, case):
    title = case["title"]

    if '（参数类型超限）' in title:
        state = eval(case['state'])
    else:
        state = case['state']

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step(f"断言抛出 ValueError,模式为{state}"):
        with pytest.raises(ValueError):
            device.mc.set_communication_state(state)

    logger.info(f"✅ 用例【{title}】异常断言通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")
