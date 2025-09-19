from time import sleep

import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot450Base
from pymycobot.error import MyCobotPro450DataException

cases = get_test_data_from_excel(Mycobot450Base.TEST_DATA_FILE, "get_error_information")

@pytest.fixture(scope="module")
def device():
    dev = Mycobot450Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    logger.info("环境清理完成，接口测试结束")

@pytest.fixture(autouse=True)
def reset_device(device):
    yield
    device.mc.clear_error_information()
    device.go_zero()

@allure.feature("获取错误信息")
@allure.story("正常状态下获取错误信息")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_get_error_information(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")

    logger.debug(f'test_api: {case["api"]}')

    with allure.step("获取错误信息"):
        response = device.mc.get_error_information()

    with allure.step("断言返回类型"):
        assert isinstance(response, int), f"返回类型错误：{type(response)}"

    with allure.step("断言返回结果"):
        allure.attach(str(case["expect_data"]),name= "期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(response),name= "实际值",attachment_type= allure.attachment_type.TEXT)
        assert response == case["expect_data"], f"断言失败，期望：{case['expect_data']}，实际：{response}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("获取错误信息")
@allure.story("奇异点异常错误信息上报")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_singular_point_error(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")

    logger.debug(f'test_api: {case["api"]}')
    logger.debug(f'target_angles: {case["target_angles"]}')
    logger.debug(f'axis: {case["axis"]}')
    logger.debug(f'target_coord: {case["target_coord"]}')

    with allure.step("机械臂运动至奇异点"):
        device.mc.send_angles(eval(case['target_angles']), device.speed)
        sleep(3)
        device.mc.send_coord(case['axis'], case['target_coord'], device.speed)
        sleep(1)
        input("请观察机械臂末端是否变蓝，点击回车继续测试")

    with allure.step("获取错误信息"):
        response = device.mc.get_error_information()

    with allure.step("断言返回类型"):
        assert isinstance(response, int), f"返回类型错误：{type(response)}"

    with allure.step("断言返回结果"):
        allure.attach(str(case["expect_data"]),name= "期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(response),name= "实际值",attachment_type= allure.attachment_type.TEXT)
        assert response == case["expect_data"], f"断言失败，期望：{case['expect_data']}，实际：{response}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")