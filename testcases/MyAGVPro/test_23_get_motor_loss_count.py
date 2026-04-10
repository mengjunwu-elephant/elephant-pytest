import time
from time import sleep

import pytest
import allure

from common1 import logger, assert_almost_equal
from common1.test_data_handler import get_test_data_from_excel
from settings import MyAGVProBase

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(MyAGVProBase.TEST_DATA_FILE, "get_motor_loss_count")


@allure.feature("查看电机丢包次数")
@allure.story("查看电机丢包次数（上电）")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "power_on"], ids=lambda c: c["title"])
def test_get_motor_loss_count1(device, case):
    title = case["title"]
    expected = eval(case["expect_data"])

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("小车上电"):
        device.mc.power_on()

    with allure.step("调用 get_motor_loss_count 接口"):
        response = device.mc.get_motor_loss_count()
        logger.debug(f"接口返回：{response}")

    with allure.step("断言返回值类型为 list"):
        assert isinstance(response, list), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言返回值list长度"):
        assert len(response) == case['list_len'], f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言读取接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("查看电机丢包次数")
@allure.story("查看电机丢包次数（下电）")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "power_off"], ids=lambda c: c["title"])
def test_get_motor_loss_count2(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("小车下电"):
        device.mc.power_off()

    with allure.step("调用 get_motor_loss_count 接口"):
        response = device.mc.get_motor_loss_count()
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
