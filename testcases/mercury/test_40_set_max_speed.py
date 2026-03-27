import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "set_max_speed")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置最大速度")
@allure.story("正常设置")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_max_speed_normal(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"API: {case['api']}")
    logger.debug(f"参数: {case['parameter']}，模式: {case['mode']}")

    with allure.step("发送 set_max_speed 指令"):
        response = device.mc.set_max_speed(case['mode'], case['parameter'])

    with allure.step("响应类型断言"):
        assert isinstance(response, int), f"机械臂返回类型应为 int，实际为 {type(response)}"

    with allure.step("响应值断言"):
        assert response == case['l_expect_data'], f"机械臂返回值不符，期望：{case['l_expect_data']}，实际：{response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("设置最大速度")
@allure.story("异常设置")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_max_speed_exception(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"API: {case['api']}")
    logger.debug(f"参数: {case['parameter']}，模式: {case['mode']}")

    with allure.step("断言抛出 MercuryDataException"):
        with pytest.raises(MercuryDataException,match=".*") as exc_info:
            device.mc.set_max_speed(case["mode"], case["parameter"])

    logger.info(f"✅ 用例【{case['title']}】触发了预期异常: {exc_info.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("设置最大速度")
@allure.story("最大速度参数是否保存")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "save_or_not"], ids=lambda c: c["title"])
def test_save_or_not(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"API: {case['api']}")
    logger.debug(f"参数: {case['parameter']}，模式: {case['mode']}")

    with allure.step("设置限位开关参数"):
        device.mc.set_max_speed(case['mode'], case['parameter'])

    with allure.step("重启机械臂"):
        device.reset()

    with allure.step("读取最大速度配置参数"):
        res = device.mc.get_max_speed(case['mode'])

    with allure.step("断言保存/未保存结果"):
        assert res == case["l_expect_data"], f"机械臂限位读取值错误：{res}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("设置最大速度")
@allure.story("仅上电调用 set_max_speed 接口")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_on_only"], ids=lambda c: c["title"])
def test_power_on_only(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"API: {case['api']}")
    logger.debug(f"参数: {case['parameter']}，模式: {case['mode']}")

    with allure.step("机械臂仅上电"):
        device.power_on_only()

    with allure.step("发送 set_max_speed 指令（机械臂）"):
        response = device.mc.set_max_speed(case['mode'], case['parameter'])

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

@allure.feature("设置最大速度")
@allure.story("下电调用 set_max_speed 接口")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_off"], ids=lambda c: c["title"])
def test_power_off(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"API: {case['api']}")
    logger.debug(f"参数: {case['parameter']}，模式: {case['mode']}")

    with allure.step("机械臂下电"):
        device.power_off()

    with allure.step("发送 set_max_speed 指令（机械臂）"):
        response = device.mc.set_max_speed(case['mode'], case['parameter'])

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


