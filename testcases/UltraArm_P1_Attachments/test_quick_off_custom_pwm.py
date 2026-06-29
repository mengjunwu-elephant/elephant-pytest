# -*- coding: utf-8 -*-
import allure
import pytest
from pymycobot.error import ultraArmP1DataException

from common1 import logger
from common1.operator_input import prompt_continue
from common1.test_data_handler import get_test_data_from_excel
from settings import UltraArmP1Base

cases = get_test_data_from_excel(UltraArmP1Base.ATTACHMENTS_TEST_DATA_FILE, "quick_off_custom_pwm")

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
@allure.story("quick_off_custom_pwm 开关自定义PWM")
@pytest.mark.parametrize(
    "case",
    [c for c in cases if c["test_type"] in ("normal", "normal_off")],
    ids=lambda c: c["title"],
)
def test_quick_off_custom_pwm(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'state:{case["state"]}')

    with allure.step(f"调用 {case['api']}（pymycobot: set_pwm_custom_mode）"):
        response = device.mc.set_pwm_custom_mode(int(case["state"]))
        logger.debug(f"接口返回：{response}")

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        if str(expected).lower() == "ok":
            assert str(response).lower() in ("ok", "1"), (
                f"用例【{title}】断言失败，期望 ok，实际 {response!r}"
            )
        else:
            assert response == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("PWM激光")
@allure.story("quick_off_custom_pwm 参数越界")
@pytest.mark.parametrize(
    "case",
    [c for c in cases if c.get("test_type") == "exception"],
    ids=lambda c: c["title"],
)
def test_quick_off_custom_pwm_exception(device, case):
    title = case["title"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'state:{case["state"]}')

    with allure.step(f"断言抛出 ultraArmP1DataException, state: {case['state']}"):
        with pytest.raises(ultraArmP1DataException) as exc:
            device.mc.set_pwm_custom_mode(int(case["state"]))

    logger.info(f"✅ 用例【{title}】异常断言通过,异常信息：{exc.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")
