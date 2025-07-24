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
    dev.ml.power_on()
    dev.mr.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mr.power_off()
    dev.ml.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("设置控制模式")
@allure.story("正常设置控制模式")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_control_mode_normal(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    param = case['parameter']

    with allure.step("发送 set_control_mode 指令"):
        l_response = device.ml.set_control_mode(param)
        r_response = device.mr.set_control_mode(param)

    with allure.step("断言返回值类型是否符合预期"):
        assert isinstance(l_response, int), f"左臂响应类型错误: {type(l_response)}"
        assert isinstance(r_response, int), f"右臂响应类型错误: {type(r_response)}"

    with allure.step("断言返回值是否符合预期"):
        allure.attach(str(case['l_expect_data']), name="左臂期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(case['r_expect_data']), name="右臂期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(l_response), name="左臂实际值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(r_response), name="右臂实际值", attachment_type=allure.attachment_type.TEXT)

        assert l_response == case['l_expect_data'], f"左臂控制模式不一致，期望: {case['l_expect_data']}，实际: {l_response}"
        assert r_response == case['r_expect_data'], f"右臂控制模式不一致，期望: {case['r_expect_data']}，实际: {r_response}"

    logger.info(f"✅ 用例【{case['title']}】测试通过")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

@allure.feature("设置控制模式")
@allure.story("异常值设置控制模式")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_control_mode_invalid(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    param = case['parameter']

    with allure.step("断言设置控制模式触发 MercuryDataException"):
        with pytest.raises(MercuryDataException, match=".*") as exc_info:
            device.ml.set_control_mode(param)
            device.mr.set_control_mode(param)

    logger.info(f"✅ 用例【{case['title']}】正确抛出异常: {exc_info.value}")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

@allure.feature("设置控制模式")
@allure.story("控制模式是否保存")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "save_or_not"], ids=lambda c: c["title"])
def test_set_control_mode_save_or_not(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    param = case['parameter']

    with allure.step("设置控制模式"):
        l_response = device.ml.set_control_mode(param)
        r_response = device.mr.set_control_mode(param)

    with allure.step("重启设备"):
        device.reset()

    with allure.step("获取控制模式状态"):
        l_get_res = device.ml.get_control_mode()
        r_get_res = device.mr.get_control_mode()

    with allure.step("断言返回值类型是否符合预期"):
        assert isinstance(l_response, int), f"左臂响应类型错误: {type(l_response)}"
        assert isinstance(r_response, int), f"右臂响应类型错误: {type(r_response)}"

    with allure.step("断言返回值是否符合预期"):
        allure.attach(str(case['l_expect_data']), name="左臂期望值",attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(case['r_expect_data']), name="右臂期望值",attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(l_get_res), name="左臂实际值",attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(r_get_res), name="右臂实际值",attachment_type=allure.attachment_type.TEXT)

        assert l_get_res == case['l_expect_data'], f"左臂控制模式不一致，期望: {case['l_expect_data']}，实际: {l_get_res}"
        assert r_get_res == case['r_expect_data'], f"右臂控制模式不一致，期望: {case['r_expect_data']}，实际: {r_get_res}"

    logger.info(f"✅ 用例【{case['title']}】测试通过")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")