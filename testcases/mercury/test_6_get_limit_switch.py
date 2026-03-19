import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_limit_switch")

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
def reset_after_test(device):
    yield
    device.reset()

@allure.feature("限位开关获取")
@allure.story("上电-限位开关获取")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_on"], ids=lambda c: c["title"])
def test_get_limit_switch_power_on(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"接口: {case['api']}, 参数: {case['parameter']}")

    with allure.step("机械臂请求限位开关状态"):
        response = device.mc.get_limit_switch()
    with allure.step("机械臂断言返回结果类型"):
        assert isinstance(response, list), f"机械臂返回类型错误: {type(response)}"
    with allure.step("机械臂断言返回响应结果"):
        allure.attach(str(response), name="机械臂实际值", attachment_type=allure.attachment_type.TEXT)
    with allure.step("机械臂断言返回响应结果"):
        allure.attach(str(case['l_expect_data']), name="机械臂期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == eval(case['l_expect_data']), f"机械臂结果断言失败，期望：{case['l_expect_data']}，实际：{response}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("限位开关获取")
@allure.story("仅上电-限位开关获取")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_on_only"], ids=lambda c: c["title"])
def test_get_limit_switch_power_on_only(device, case):
    title = case["title"]
    # 进入仅上电模式
    device.power_on_only()
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"接口: {case['api']}, 参数: {case['parameter']}")

    with allure.step("机械臂请求限位开关状态"):
        response = device.mc.get_limit_switch()
    with allure.step("机械臂断言返回结果类型"):
        allure.attach(str(response), name="机械臂实际值", attachment_type=allure.attachment_type.TEXT)
    with allure.step("机械臂断言返回结果类型"):
        allure.attach(str(case['l_expect_data']), name="机械臂期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == case['l_expect_data'], f"机械臂结果断言失败，期望：{case['l_expect_data']}，实际：{response}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("限位开关获取")
@allure.story("断电-限位开关获取")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_off"], ids=lambda c: c["title"])
def test_get_limit_switch_power_off(device, case):
    title = case["title"]
    # 进入断电模式
    device.mc.power_off()

    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"接口: {case['api']}, 参数: {case['parameter']}")

    with allure.step("机械臂请求限位开关状态"):
        response = device.mc.get_limit_switch()
    with allure.step("机械臂断言返回结果类型"):
        allure.attach(str(response), name="机械臂实际值", attachment_type=allure.attachment_type.TEXT)
    with allure.step("机械臂断言返回结果类型"):
        allure.attach(str(case['l_expect_data']), name="机械臂期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == case['l_expect_data'], f"机械臂结果断言失败，期望：{case['l_expect_data']}，实际：{response}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")
