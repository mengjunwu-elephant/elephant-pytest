import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 读取测试数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "clear_error_information")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@pytest.fixture(autouse=True)
def reset_device(device):
    yield
    device.mc.clear_error_information()
    device.go_zero()

@allure.feature("错误信息清除接口")
@allure.story("奇异点错误清除")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal1"], ids=lambda c: c["title"])
def test_clear_error_information_with_error(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")

    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameter: {case['parameter']}")

    with allure.step("使机械臂进入奇异点位置"):
        device.mc.send_angles([0, 0, 0, -20, 0, 0, 0], device.speed)
        device.mc.send_angles([0, 0, 0, -20, 0, 180, 0], device.speed)
        device.mc.send_coord(3, 300, device.speed)

    with allure.step("机械臂清除错误信息"):
        response = device.mc.clear_error_information()
    with allure.step("机械臂断言返回类型为 int"):
        assert isinstance(response, int), f"机械臂返回类型错误：{type(response)}"
    with allure.step("机械臂断言返回结果"):
        allure.attach(str(case["l_expect_data"]),name= "机械臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(response),name= "机械臂实际值",attachment_type= allure.attachment_type.TEXT)
        assert response == case["l_expect_data"], f"机械臂断言失败，期望：{case['l_expect_data']}，实际：{response}"
    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("错误信息清除接口")
@allure.story("无异常状态清除")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal2"], ids=lambda c: c["title"])
def test_clear_error_information_no_error(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")

    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameter: {case['parameter']}")

    with allure.step("机械臂清除错误信息（当前无异常）"):
        response = device.mc.clear_error_information()
    with allure.step("机械臂断言返回类型为 int"):
        assert isinstance(response, int), f"机械臂返回类型错误：{type(response)}"
    with allure.step("机械臂断言返回结果"):
        allure.attach(str(case["l_expect_data"]),name= "机械臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(response),name= "机械臂实际值",attachment_type= allure.attachment_type.TEXT)
        assert response == case["l_expect_data"], f"机械臂断言失败，期望：{case['l_expect_data']}，实际：{response}"
    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")
