from time import sleep

import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger, assert_almost_equal
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "focus_servo")


@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = MercuryBase()
    dev.power_on()
    dev.go_zero()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.power_off()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("单个电机上电")
@allure.story("正确设置单个电机上电")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_focus_servo1(device, case):
    title = case["title"]
    expected = case["l_expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'joint:{case["joint"]}')

    with allure.step(f'放松机械臂'):
        device.mc.release_servo(case['joint'])
        sleep(1)

    with allure.step(f"调用 {case['api']} 接口"):
        response = device.mc.focus_servo(case["joint"])
        logger.debug(f"接口返回：{response}")

    res = input(f'{case["joint"]}关节有无锁紧,输入1未锁紧,其他锁紧')

    with allure.step("断言机械臂是否锁紧"):
        assert res != '1', f"机械臂未锁紧"

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("单个电机上电")
@allure.story("超限参数验证")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_focus_servo_exception(device, case):
    title = case["title"]
    expected = case["l_expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'joint:{case["joint"]}')

    with allure.step(f"断言抛出 MercuryDataException,关节为{case['joint']}"):
        with pytest.raises(MercuryDataException):
            device.mc.focus_servo(case["joint"])

    logger.info(f"✅ 用例【{title}】异常断言通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("单个电机上电")
@allure.story("仅上电调用")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_on_only"], ids=lambda c: c["title"])
def test_power_on_only(device, case):
    title = case["title"]
    expected = case["l_expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("机械臂仅上电"):
        device.power_on_only()

    with allure.step(f"调用 {case['api']} 接口"):
        response = device.mc.focus_servo(case["joint"])
        logger.debug(f"接口返回：{response}")

    with allure.step("机械臂断言返回类型"):
        assert response is None, f"机械臂返回类型错误，期望None，实际{type(response)}"

    with allure.step("断言返回值是否匹配预期"):
        allure.attach(str(case["l_expect_data"]), name="机械臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际", attachment_type=allure.attachment_type.TEXT)
        assert expected == response, f"机械臂响应不一致，期望: {expected}，实际: {response}"

    with allure.step("机械臂上电"):
        device.power_on()

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("单个电机上电")
@allure.story("下电调用")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_off"], ids=lambda c: c["title"])
def test_power_off(device, case):
    title = case["title"]
    expected = case["l_expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("机械臂下电"):
        device.power_off()

    with allure.step(f"调用 {case['api']} 接口"):
        response = device.mc.focus_servo(case["joint"])
        logger.debug(f"接口返回：{response}")

    with allure.step("机械臂断言返回类型"):
        assert response is None, f"机械臂返回类型错误，期望None，实际{type(response)}"

    with allure.step("断言返回值是否匹配预期"):
        allure.attach(str(case["l_expect_data"]), name="机械臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际", attachment_type=allure.attachment_type.TEXT)
        assert expected == response, f"机械臂响应不一致，期望: {expected}，实际: {response}"

    with allure.step("机械臂上电"):
        device.power_on()

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")
