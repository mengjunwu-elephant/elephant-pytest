import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "jog_increment_coord")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.go_zero()
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@pytest.fixture(autouse=True)
def init_coords_before_each_case(device):
    device.init_coords()
    yield

@allure.feature("机械臂Jog增量坐标接口")
@allure.story("正常增量坐标Jog")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_jog_increment_coord_normal(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"API: {case['api']}, Axis: {case['axis']}, Parameter: {case['parameter']}, Speed: {case['speed']}")

    with allure.step("机械臂发送 jog_increment_coord 指令"):
        response = device.mc.jog_increment_coord(case["axis"], case["parameter"], case["speed"])
    with allure.step("断言机械臂响应类型与值"):
        assert isinstance(response, int), f"机械臂返回类型应为 int，实际为 {type(response)}"
        assert response == case["l_expect_data"], f"机械臂返回值不符，期望：{case['l_expect_data']}，实际：{response}"
    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("机械臂Jog增量坐标接口")
@allure.story("异常参数测试")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_jog_increment_coord_exception(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试异常场景《《《")
    logger.debug(f"API: {case['api']}, Axis: {case['axis']}, Parameter: {case['parameter']}, Speed: {case['speed']}")

    with allure.step("机械臂发送 jog_increment_coord 异常请求，断言抛异常"):
        with pytest.raises(MercuryDataException) as exc_info:
            device.mc.jog_increment_coord(case["axis"], case["parameter"], case["speed"])

    logger.info(f"✅ 用例【{case['title']}】触发了预期异常: {exc_info.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("机械臂Jog增量坐标接口")
@allure.story("仅上电 jog_increment_coord 运动")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_on_only"], ids=lambda c: c["title"])
def test_power_on_only(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"API: {case['api']}, Axis: {case['axis']}, Parameter: {case['parameter']}, Speed: {case['speed']}")

    with allure.step("机械臂仅上电"):
        device.power_on_only()

    with allure.step("发送 jog_increment_coord 指令（机械臂）"):
        response = device.mc.jog_increment_coord(case["axis"], case["parameter"], case["speed"])

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"机械臂返回类型错误: {type(response)}"

    with allure.step("断言返回值是否匹配预期"):
        allure.attach(str(case["l_expect_data"]), name="机械臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际", attachment_type=allure.attachment_type.TEXT)
        assert case["l_expect_data"] == response, f"机械臂响应不一致，期望: {case['l_expect_data']}，实际: {response}"

    with allure.step("机械臂上电"):
        device.power_on()

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("机械臂Jog增量坐标接口")
@allure.story("下电 jog_increment_coord 运动")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_off"], ids=lambda c: c["title"])
def test_power_off(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"API: {case['api']}, Axis: {case['axis']}, Parameter: {case['parameter']}, Speed: {case['speed']}")

    with allure.step("机械臂下电"):
        device.power_off()

    with allure.step("发送 jog_increment_coord 指令（机械臂）"):
        response = device.mc.jog_increment_coord(case["axis"], case["parameter"], case["speed"])

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"机械臂返回类型错误: {type(response)}"

    with allure.step("断言返回值是否匹配预期"):
        allure.attach(str(case["l_expect_data"]), name="机械臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际", attachment_type=allure.attachment_type.TEXT)
        assert case["l_expect_data"] == response, f"机械臂响应不一致，期望: {case['l_expect_data']}，实际: {response}"

    with allure.step("机械臂上电"):
        device.power_on()

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")