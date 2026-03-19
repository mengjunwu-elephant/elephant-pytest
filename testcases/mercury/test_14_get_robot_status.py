import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_robot_status")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("机器人状态查询接口")
@allure.story("上电状态查询")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_on"], ids=lambda c: c["title"])
def test_get_robot_status_power_on(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameter: {case['parameter']}")

    with allure.step("查询机械臂状态"):
        response = device.mc.get_robot_status()
    with allure.step("机械臂断言返回类型为 list"):
        assert isinstance(response, list), f"机械臂返回类型错误：{type(response)}"
    with allure.step("机械臂断言返回结果"):
        allure.attach(str(case["l_expect_data"]),name= "机械臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(response),name= "机械臂实际值",attachment_type= allure.attachment_type.TEXT)
        assert response == eval(case["l_expect_data"]), f"机械臂断言失败，期望：{case['l_expect_data']}，实际：{response}"
    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("机器人状态查询接口")
@allure.story("仅上电状态查询")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_on_only"], ids=lambda c: c["title"])
def test_get_robot_status_power_on_only(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameter: {case['parameter']}")

    with allure.step("设置机械臂为仅上电模式"):
        device.power_on_only()

    with allure.step("查询机械臂状态"):
        response = device.mc.get_robot_status()
    with allure.step("机械臂断言返回类型为 list"):
        assert isinstance(response, list), f"机械臂返回类型错误：{type(response)}"
    with allure.step("机械臂断言返回结果"):
        allure.attach(str(case["l_expect_data"]),name= "机械臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(response),name= "机械臂实际值",attachment_type= allure.attachment_type.TEXT)
        assert response == eval(case["l_expect_data"]), f"机械臂断言失败，期望：{case['l_expect_data']}，实际：{response}"
    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")
