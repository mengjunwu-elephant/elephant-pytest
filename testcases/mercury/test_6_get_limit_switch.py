import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_limit_switch")


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

    with allure.step("左臂请求限位开关状态"):
        l_response = device.ml.get_limit_switch()

    with allure.step("右臂请求限位开关状态"):
        r_response = device.mr.get_limit_switch()

    with allure.step("左臂断言返回结果类型"):
        assert isinstance(l_response, list), f"左臂返回类型错误: {type(l_response)}"
    with allure.step("右臂断言返回结果类型"):
        assert isinstance(r_response, list), f"右臂返回类型错误: {type(r_response)}"

    with allure.step("左臂断言返回响应结果"):
        allure.attach(str(case['r_expect_data']), name="左臂期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(l_response), name="左臂实际值", attachment_type=allure.attachment_type.TEXT)
        assert r_response == eval(case['r_expect_data']), f"右臂结果断言失败，期望：{case['r_expect_data']}，实际：{r_response}"
    with allure.step("右臂断言返回响应结果"):
        allure.attach(str(case['l_expect_data']), name="右臂期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(l_response), name="右臂实际值", attachment_type=allure.attachment_type.TEXT)
        assert l_response == eval(case['l_expect_data']), f"左臂结果断言失败，期望：{case['l_expect_data']}，实际：{l_response}"

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

    with allure.step("左臂请求限位开关状态"):
        l_response = device.ml.get_limit_switch()

    with allure.step("右臂请求限位开关状态"):
        r_response = device.mr.get_limit_switch()

    with allure.step("左臂断言返回结果类型"):
        allure.attach(str(case['r_expect_data']), name="左臂期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(l_response), name="左臂实际值", attachment_type=allure.attachment_type.TEXT)
        assert r_response == case['r_expect_data'], f"右臂结果断言失败，期望：{case['r_expect_data']}，实际：{r_response}"
    with allure.step("右臂断言返回结果类型"):
        allure.attach(str(case['l_expect_data']), name="右臂期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(l_response), name="右臂实际值", attachment_type=allure.attachment_type.TEXT)
        assert l_response == case['l_expect_data'], f"左臂结果断言失败，期望：{case['l_expect_data']}，实际：{l_response}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("限位开关获取")
@allure.story("断电-限位开关获取")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_off"], ids=lambda c: c["title"])
def test_get_limit_switch_power_off(device, case):
    title = case["title"]
    # 进入断电模式
    device.mr.power_off()
    device.ml.power_off()

    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"接口: {case['api']}, 参数: {case['parameter']}")

    with allure.step("左臂请求限位开关状态"):
        l_response = device.ml.get_limit_switch()

    with allure.step("右臂请求限位开关状态"):
        r_response = device.mr.get_limit_switch()

    with allure.step("左臂断言返回结果类型"):
        allure.attach(str(case['r_expect_data']), name="左臂期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(l_response), name="左臂实际值", attachment_type=allure.attachment_type.TEXT)
        assert r_response == case['r_expect_data'], f"右臂结果断言失败，期望：{case['r_expect_data']}，实际：{r_response}"
    with allure.step("右臂断言返回结果类型"):
        allure.attach(str(case['l_expect_data']), name="右臂期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(l_response), name="右臂实际值", attachment_type=allure.attachment_type.TEXT)
        assert l_response == case['l_expect_data'], f"左臂结果断言失败，期望：{case['l_expect_data']}，实际：{l_response}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")
