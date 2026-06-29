# -*- coding: utf-8 -*-
import time

import allure
import pytest
from pymycobot.error import ultraArmP1DataException

from common1 import logger
from common1.operator_input import prompt_continue
from common1.test_data_handler import get_test_data_from_excel
from settings import UltraArmP1Base

cases = get_test_data_from_excel(UltraArmP1Base.ATTACHMENTS_TEST_DATA_FILE, "set_pump_state")

@pytest.fixture(scope="module", autouse=True)
def confirm_pump_module_connected(device):
    prompt_continue("请确认吸泵模块已连接，按回车继续")
    yield

@allure.feature("设置吸泵状态")
@allure.story("正常用例 - 打开吸泵")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_set_pump_state_normal(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'pump_state:{case["pump_state"]}')

    with allure.step(f"调用 {case['api']} 接口"):
        response = device.mc.set_pump_state(case["pump_state"])
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

@allure.feature("设置吸泵状态")
@allure.story("正常用例 - 释放吸泵")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal_release"], ids=lambda c: c["title"])
def test_set_pump_state_normal_release(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'pump_state:{case["pump_state"]}')

    with allure.step(f"调用 {case['api']} 接口"):
        response = device.mc.set_pump_state(case["pump_state"])
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

@allure.feature("设置吸泵状态")
@allure.story("正常用例 - 关闭吸泵")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal_close"], ids=lambda c: c["title"])
def test_set_pump_state_normal_close(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'pump_state:{case["pump_state"]}')

    with allure.step(f"调用 {case['api']} 接口"):
        response = device.mc.set_pump_state(case["pump_state"])
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

@allure.feature("设置吸泵状态")
@allure.story("异常用例 - 吸泵状态越界")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_pump_state_exception(device, case):
    title = case["title"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'pump_state:{case["pump_state"]}')

    with allure.step(f"断言抛出 ultraArmP1DataException, pump_state: {case['pump_state']}"):
        with pytest.raises(ultraArmP1DataException) as exc:
            device.mc.set_pump_state(case["pump_state"])

    logger.info(f"✅ 用例【{title}】异常断言通过,异常信息：{exc.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")
