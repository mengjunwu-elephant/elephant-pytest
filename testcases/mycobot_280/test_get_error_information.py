from time import sleep

import pytest
import allure
from common1 import logger
from common1.etest_data_handler import get_test_data_from_excel
from settings import *

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(Mycobot280Base.TEST_DATA_FILE, "get_error_information")

@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = Mycobot280Base()
    dev.default_settings()
    if dev.is_moving():
        logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.clear_error_information()
    dev.mc.close()
    logger.info("环境清理完成，接口测试结束")

# @allure.feature("固件版本获取")
@allure.story("获取报错信息")
@pytest.mark.parametrize("case", cases, ids=[case["title"] for case in cases])
def test_get_basic_version(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    # 控制J4到限位值，触发异常场景，返回自干涉错误信息19
    if case["test_type"]=="exception":
        device.mc.send_angle(4,-145,50)
        if device.is_moving():
            response= device.mc.get_error_information()

    with allure.step("调用 get_error_information 接口"):
        response = device.mc.get_error_information()
        logger.debug(f"接口返回：{response}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误，应为 int，实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')