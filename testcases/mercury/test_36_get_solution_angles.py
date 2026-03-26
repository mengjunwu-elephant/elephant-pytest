import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 读取 Excel 测试用例
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_solution_angles")

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
def reset_position(device):
    device.init_coords()
    yield

@allure.feature("解算角度接口")
@allure.story("获取机械臂解算角度")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_get_solution_angles(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"API: {case['api']}, Parameter: {case['parameter']}")

    with allure.step("发送 set_solution_angles 指令"):
        device.mc.set_solution_angles(case["l_expect_data"], device.speed)

    with allure.step("调用 get_solution_angles 接口"):
        response = device.mc.get_solution_angles()

    with allure.step("断言返回类型"):
        assert isinstance(response, float), f"机械臂返回类型应为 float，实际为 {type(response)}"

    with allure.step("断言返回值"):
        assert response == case["l_expect_data"], f"机械臂返回值不符，期望：{case['l_expect_data']}，实际：{response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("解算角度接口")
@allure.story("仅上电调用 get_solution_angles 接口")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_on_only"], ids=lambda c: c["title"])
def test_power_on_only(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"API: {case['api']}, Parameter: {case['parameter']}")

    with allure.step("机械臂仅上电"):
        device.power_on_only()

    with allure.step("发送 get_solution_angles 指令（机械臂）"):
        response = device.mc.get_solution_angles()

    with allure.step("机械臂断言返回类型"):
        assert response is None, f"机械臂返回类型错误，期望None，实际{type(response)}"

    with allure.step("断言返回值是否匹配预期"):
        allure.attach(str(case["l_expect_data"]), name="机械臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际", attachment_type=allure.attachment_type.TEXT)
        assert case["l_expect_data"] == response, f"机械臂响应不一致，期望: {case['l_expect_data']}，实际: {response}"

    with allure.step("机械臂上电"):
        device.power_on()

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("解算角度接口")
@allure.story("下电调用 get_solution_angles 接口")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_off"], ids=lambda c: c["title"])
def test_power_off(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"API: {case['api']}, Parameter: {case['parameter']}")

    with allure.step("机械臂下电"):
        device.power_off()

    with allure.step("发送 get_solution_angles 指令（机械臂）"):
        response = device.mc.get_solution_angles()

    with allure.step("机械臂断言返回类型"):
        assert response is None, f"机械臂返回类型错误，期望None，实际{type(response)}"

    with allure.step("断言返回值是否匹配预期"):
        allure.attach(str(case["l_expect_data"]), name="机械臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际", attachment_type=allure.attachment_type.TEXT)
        assert case["l_expect_data"] == response, f"机械臂响应不一致，期望: {case['l_expect_data']}，实际: {response}"

    with allure.step("机械臂上电"):
        device.power_on()

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")
