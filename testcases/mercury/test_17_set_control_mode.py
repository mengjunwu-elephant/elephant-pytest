import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 获取数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "set_control_mode")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置控制模式")
@allure.story("正常设置控制模式")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_control_mode_normal(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    param = case['parameter']

    with allure.step("机械臂发送 set_control_mode 指令"):
        response = device.mc.set_control_mode(param)
    with allure.step("机械臂断言返回类型"):
        assert isinstance(response, int), f"机械臂响应类型错误: {type(response)}"
    with allure.step("机械臂断言返回结果"):
        allure.attach(str(case['l_expect_data']), name="机械臂期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == case['l_expect_data'], f"机械臂控制模式不一致，期望: {case['l_expect_data']}，实际: {response}"
    logger.info(f"✅ 用例【{case['title']}】测试通过")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

@allure.feature("设置控制模式")
@allure.story("异常值设置控制模式")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_control_mode_invalid(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    param = case['parameter']

    with allure.step("机械臂设置控制模式超限"):
        with pytest.raises(MercuryDataException, match=".*"):
            device.mc.set_control_mode(param)

    with allure.step("机械臂设置控制模式超限"):
        with pytest.raises(MercuryDataException, match=".*") as exc_info:
            device.mc.set_control_mode(param)

    logger.info(f"✅ 用例【{case['title']}】触发了预期异常: {exc_info.value}")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

@allure.feature("设置控制模式")
@allure.story("控制模式是否保存")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "save_or_not"], ids=lambda c: c["title"])
def test_set_control_mode_save_or_not(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    param = case['parameter']

    with allure.step("机械臂设置控制模式"):
        response = device.mc.set_control_mode(param)
    with allure.step("重启设备"):
        device.reset()

    with allure.step("机械臂获取控制模式状态"):
        get_res = device.mc.get_control_mode()
    with allure.step("机械臂断言返回值类型"):
        assert isinstance(response, int), f"机械臂响应类型错误: {type(response)}"
    with allure.step("机械臂断言返回结果"):
        allure.attach(str(case['l_expect_data']), name="机械臂期望值",attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="机械臂实际值",attachment_type=allure.attachment_type.TEXT)
        assert get_res == case['l_expect_data'], f"机械臂控制模式不一致，期望: {case['l_expect_data']}，实际: {get_res}"
    logger.info(f"✅ 用例【{case['title']}】测试通过")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

@allure.feature("设置控制模式")
@allure.story("仅上电设置控制模式")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_on_only"], ids=lambda c: c["title"])
def test_power_on_only(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")

    logger.debug(f'test_api: {case["api"]}')
    logger.debug(f'test_parameter: {case["parameter"]}')

    with allure.step("机械臂仅上电"):
        device.power_on_only()

    with allure.step("机械臂获取错误信息"):
        response = device.mc.set_control_mode(case['parameter'])
    with allure.step("机械臂断言返回类型"):
        assert response is None, f"机械臂返回类型错误，期望None，实际{type(response)}"
    with allure.step("机械臂断言返回结果"):
        allure.attach(str(case["l_expect_data"]),name= "机械臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(response),name= "机械臂实际值",attachment_type= allure.attachment_type.TEXT)
        assert response == case["l_expect_data"], f"机械臂断言失败，期望：{case['l_expect_data']}，实际：{response}"
    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("设置控制模式")
@allure.story("下电设置控制模式")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_off"], ids=lambda c: c["title"])
def test_power_off(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")

    logger.debug(f'test_api: {case["api"]}')
    logger.debug(f'test_parameter: {case["parameter"]}')

    with allure.step("机械臂下电"):
        device.power_off()

    with allure.step("机械臂获取错误信息"):
        response = device.mc.set_control_mode(case['parameter'])
    with allure.step("机械臂断言返回类型"):
        assert response is None, f"机械臂返回类型错误，期望None，实际{type(response)}"
    with allure.step("机械臂断言返回结果"):
        allure.attach(str(case["l_expect_data"]),name= "机械臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(response),name= "机械臂实际值",attachment_type= allure.attachment_type.TEXT)
        assert response == case["l_expect_data"], f"机械臂断言失败，期望：{case['l_expect_data']}，实际：{response}"
    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")