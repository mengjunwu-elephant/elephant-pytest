import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 获取全部测试用例数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_atom_version")

@pytest.fixture(scope="module")
def device():
    """设备初始化：机械臂上电"""
    dev = MercuryBase()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("获取Atom版本号")
@allure.story("上电 - 获取Atom版本号")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_on"], ids=lambda c: c["title"])
def test_get_atom_version_power_on(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameter: {case['parameter']}")

    device.reset()

    with allure.step("机械臂发送请求"):
        response = device.mc.get_atom_version()
        logger.debug(f"机械臂响应：{response}")

    with allure.step("机械臂断言响应数据类型为 float"):
        assert isinstance(response, float), f"机械臂返回值类型错误，应为 float，实际为 {type(response)}"

    with allure.step("机械臂断言响应结果"):
        allure.attach(str(case['l_expect_data']), name="机械臂期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == case['l_expect_data'], f"机械臂断言失败：期望 {case['l_expect_data']}，实际 {response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    device.reset()
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("获取Atom版本号")
@allure.story("仅上电 - 获取Atom版本号")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_on_only"], ids=lambda c: c["title"])
def test_get_atom_version_power_on_only(device, case):
    device.power_on_only()
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameter: {case['parameter']}")

    with allure.step("发送请求"):
        response = device.mc.get_atom_version()

    with allure.step("机械臂断言响应为 None"):
        assert response is None, f"机械臂返回值应为 None，实际为 {response}"

    with allure.step("机械臂断言响应结果"):
        allure.attach(str(case['l_expect_data']), name="机械臂期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == case['l_expect_data'],f'机械臂断言失败：期望 {case["l_expect_data"]}，实际 {response}'

    logger.info(f"✅ 用例【{title}】测试通过")
    device.reset()
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("获取Atom版本号")
@allure.story("断电 - 获取Atom版本号")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_off"], ids=lambda c: c["title"])
def test_get_atom_version_power_off(device, case):
    device.power_off()
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameter: {case['parameter']}")

    with allure.step("发送请求"):
        response = device.mc.get_atom_version()

    with allure.step("机械臂断言响应为 None"):
        assert response is None, f"机械臂返回值应为 None，实际为 {response}"

    with allure.step("断言响应结果"):
        allure.attach(str(case['l_expect_data']), name="机械臂期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == case['l_expect_data'],f'机械臂断言失败：期望 {case["l_expect_data"]}，实际 {response}'

    logger.info(f"✅ 用例【{title}】测试通过")
    device.reset()
    logger.info(f"》》》用例【{title}】测试完成《《《")
