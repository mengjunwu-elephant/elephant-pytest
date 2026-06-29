# -*- coding: utf-8 -*-
import ast

import allure
import pytest

from common1 import logger
from common1.operator_input import prompt_continue
from common1.test_data_handler import get_test_data_from_excel
from settings import UltraArmP1Base

cases = get_test_data_from_excel(UltraArmP1Base.ATTACHMENTS_TEST_DATA_FILE, "get_pwm_status")

@pytest.fixture(scope="module", autouse=True)
def confirm_pwm_module_connected(device):
    prompt_continue("请确认激光/PWM模块已连接，按回车继续")
    yield

@pytest.fixture(scope="module", autouse=True)
def teardown_pwm_modes(device):
    yield
    with allure.step("测试模块结束：关闭激光PWM与自定义PWM模式"):
        try:
            device.mc.set_pwm_laser_mode(0)
            device.mc.set_pwm_custom_mode(0)
            logger.info("模块收尾已调用 set_pwm_laser_mode(0) 与 set_pwm_custom_mode(0)")
        except Exception as e:
            logger.warning(f"模块收尾关闭PWM模式异常：{e}")

@allure.feature("PWM激光")
@allure.story("get_pwm_status 读取PWM状态")
@pytest.mark.parametrize(
    "case",
    [c for c in cases if c["test_type"] == "normal"],
    ids=lambda c: c["title"],
)
def test_get_pwm_status(device, case):
    title = case["title"]
    expected = ast.literal_eval(str(case["expect_data"]))

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'expect_data:{case["expect_data"]}')

    with allure.step("预置PWM为关闭状态"):
        device.mc.set_pwm_laser_mode(0)
        device.mc.set_pwm_custom_mode(0)

    with allure.step(f"调用 {case['api']} 接口"):
        response = device.mc.get_pwm_status()
        logger.debug(f"接口返回：{response}")

    with allure.step("断言返回值类型为 list"):
        assert isinstance(response, list), f"返回类型错误，应为 list，实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')
