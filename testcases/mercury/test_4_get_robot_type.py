import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 读取Excel测试数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_robot_type")


@pytest.fixture(scope="module")
def device():
    """设备初始化：左臂上电 -> 右臂上电"""
    dev = MercuryBase()
    dev.ml.power_on()
    dev.mr.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mr.power_off()
    dev.ml.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("获取机械臂类型")
@allure.story("上电 - 获取机械臂类型")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_on"], ids=lambda c: c["title"])
def test_get_robot_type_power_on(device, case):
    title = case['title']
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameters: {case['parameters']}")
    device.reset()

    with allure.step("发送请求"):
        l_response = device.ml.get_robot_type()
        r_response = device.mr.get_robot_type()

    with allure.step("左臂断言类型为 int"):
        assert isinstance(l_response, int), f"左臂响应类型错误，应为 int，实际为 {type(l_response)}"
    with allure.step("右臂断言类型为 int"):
        assert isinstance(r_response, int), f"右臂响应类型错误，应为 int，实际为 {type(r_response)}"

    with allure.step("左臂断言结果值"):
        allure.attach(str(case['l_expect_data']), name="左臂期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(l_response),name='左臂实际值',attachment_type=allure.attachment_type.TEXT)
        assert l_response == case["l_expect_data"], f"左臂期望值 {case['l_expect_data']}，实际值 {l_response}"
    with allure.step("右臂断言结果值"):
        allure.attach(str(case['r_expect_data']),name = '期望值',attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(r_response),name='实际值',attachment_type=allure.attachment_type.TEXT)
        assert r_response == case["r_expect_data"], f"右臂期望值 {case['r_expect_data']}，实际值 {r_response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    device.reset()
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("获取机械臂类型")
@allure.story("仅上电 - 获取机械臂类型")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_on_only"], ids=lambda c: c["title"])
def test_get_robot_type_power_on_only(device, case):
    title = case["title"]
    device.power_on_only()
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameters: {case['parameters']}")

    with allure.step("发送请求"):
        l_response = device.ml.get_robot_type()
        r_response = device.mr.get_robot_type()

    with allure.step("左臂断言类型为 int"):
        assert isinstance(l_response, int), f"左臂响应类型错误，应为 int，实际为 {type(l_response)}"
    with allure.step("右臂断言类型为 int"):
        assert isinstance(r_response, int), f"右臂响应类型错误，应为 int，实际为 {type(r_response)}"

    with allure.step("左臂断言结果值"):
        allure.attach(str(case['l_expect_data']), name="左臂期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(l_response),name='左臂实际值',attachment_type=allure.attachment_type.TEXT)
        assert l_response == case["l_expect_data"], f"左臂期望值 {case['l_expect_data']}，实际值 {l_response}"
    with allure.step("右臂断言结果值"):
        allure.attach(str(case['r_expect_data']),name = '右臂期望值',attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(r_response),name='右臂实际值',attachment_type=allure.attachment_type.TEXT)
        assert r_response == case["r_expect_data"], f"右臂期望值 {case['r_expect_data']}，实际值 {r_response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    device.reset()
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("获取Robot类型")
@allure.story("断电 - 获取Robot类型")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_off"], ids=lambda c: c["title"])
def test_get_robot_type_power_off(device, case):
    title = case["title"]
    device.power_off()
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameters: {case['parameters']}")

    with allure.step("发送请求"):
        l_response = device.ml.get_robot_type()
        r_response = device.mr.get_robot_type()

    with allure.step("左臂断言类型为 int"):
        assert isinstance(l_response, int), f"左臂响应类型错误，应为 int，实际为 {type(l_response)}"
    with allure.step("右臂断言类型为 int"):
        assert isinstance(r_response, int), f"右臂响应类型错误，应为 int，实际为 {type(r_response)}"

    with allure.step("左臂断言结果值"):
        allure.attach(str(case['l_expect_data']), name="左臂期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(l_response),name='左臂实际值',attachment_type=allure.attachment_type.TEXT)
        assert l_response == case["l_expect_data"], f"左臂期望值 {case['l_expect_data']}，实际值 {l_response}"
    with allure.step("右臂断言结果值"):
        allure.attach(str(case['r_expect_data']),name = '期望值',attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(r_response),name='实际值',attachment_type=allure.attachment_type.TEXT)
        assert r_response == case["r_expect_data"], f"右臂期望值 {case['r_expect_data']}，实际值 {r_response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    device.reset()
    logger.info(f"》》》用例【{title}】测试完成《《《")