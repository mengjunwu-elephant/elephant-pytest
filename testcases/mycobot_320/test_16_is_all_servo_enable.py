import time
import pytest
import allure
from pymycobot.error import MyCobot320DataException
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot320Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(Mycobot320Base.TEST_DATA_FILE, "is_all_servo_enable")

normal_cases = [case for case in cases if case.get("test_type") == "normal"]
logic_cases = [case for case in cases if case.get("test_type") == "logic"]


@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = Mycobot320Base()
    logger.info("初始化完成，接口测试开始")
    dev.m.power_on()
    yield dev
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("所有关节连接状态")
@allure.story("下电用例")
@pytest.mark.parametrize("case", logic_cases, ids=[case["title"] for case in logic_cases])
def test_is_all_servo_enable1(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    device.m.power_off()
    while True:
        if device.m.is_power_on() == 0:
            break
    time.sleep(0.1)

    with allure.step("调用 is_all_servo_enable 接口"):
        response = device.m.is_all_servo_enable()
        logger.debug(f"接口返回：{response}")

    device.m.power_on()
    while True:
        if device.m.is_power_on() == 1:
            break
    time.sleep(0.1)

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("所有关节连接状态")
@allure.story("上电用例")
@pytest.mark.parametrize("case", normal_cases, ids=[case["title"] for case in normal_cases])
def test_is_all_servo_enable2(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    device.m.power_on()
    while True:
        if device.m.is_power_on() == 1:
            break
    time.sleep(0.1)

    with allure.step("调用 is_all_servo_enable 接口"):
        response = device.m.is_all_servo_enable()
        logger.debug(f"接口返回：{response}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')