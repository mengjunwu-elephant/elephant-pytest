import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 加载测试数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_control_mode")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("获取控制模式")
@allure.story("默认控制模式")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal1"], ids=lambda c: c["title"])
def test_get_control_mode_default(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")

    with allure.step("机械臂发送 get_control_mode 指令"):
        response = device.mc.get_control_mode()
    with allure.step("机械臂断言返回类型为 int"):
        assert isinstance(response, int), f"机械臂响应类型错误: {type(response)}"
    with allure.step("机械臂断言响应结果"):
        allure.attach(str(case['l_expect_data']), name="机械臂期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == case['l_expect_data'], f"机械臂控制模式不一致，期望: {case['l_expect_data']}，实际: {response}"
    logger.info(f"✅ 用例【{case['title']}】测试通过")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

@allure.feature("获取控制模式")
@allure.story("设置后控制模式查询")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal2"], ids=lambda c: c["title"])
def test_get_control_mode_after_setting(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")

    with allure.step("先切换控制模式为力矩模式 (1)"):
        device.mc.set_control_mode(1)

    with allure.step("发送 get_control_mode 指令"):
        response = device.mc.get_control_mode()

    with allure.step("机械臂断言返回类型为 int"):
        assert isinstance(response, int), f"机械臂响应类型错误: {type(response)}"
    with allure.step("机械臂断言控制模式设置后值正确"):
        allure.attach(str(case['l_expect_data']), name="机械臂期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == case['l_expect_data'], f"机械臂控制模式不一致，期望: {case['l_expect_data']}，实际: {response}"
    with allure.step("恢复控制模式并重启设备"):
        device.reset()

    logger.info(f"✅ 用例【{case['title']}】测试通过")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")
