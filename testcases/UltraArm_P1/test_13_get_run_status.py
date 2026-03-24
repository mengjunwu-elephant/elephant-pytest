import pytest
import allure
from time import sleep

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import UltraArmP1Base

# 加载测试数据
cases = get_test_data_from_excel(UltraArmP1Base.TEST_DATA_FILE, "get_run_status")


@allure.feature("检查机械臂运动状态")
@allure.story("静止状态下运动状态查询")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_get_run_status_normal(device, case):
    title = case["title"]
    expected = case["expect_data"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"接口: {case['api']}，参数: {case['parameter']}")

    with allure.step("获取运动状态"):
        response = device.mc.get_run_status()

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("检查机械臂运动状态")
@allure.story("运动状态下运动状态查询")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal1"], ids=lambda c: c["title"])
def test_get_run_status_normal1(device, case):
    title = case["title"]
    expected = case["expect_data"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"接口: {case['api']}，参数: {case['parameter']}")
    sleep(5)
    with allure.step("使机械臂运动"):
        device.mc.send_angles(device.coords_init_angles,device.speed,_async=True)
        sleep(1)

    with allure.step("获取运动状态"):
        response = device.mc.get_run_status()
        device.wait()

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")