import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "is_power_on")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    # 初始化先左臂上电，后右臂上电
    dev.ml.power_on()
    dev.mr.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    # 测试结束，依次下电并关闭设备
    dev.ml.power_off()
    dev.mr.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@pytest.fixture(autouse=True)
def reset_device(device):
    yield
    device.reset()

@allure.feature("机械臂电源状态查询")
@allure.story("查询上电状态")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_on"], ids=lambda c: c["title"])
def test_power_on(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")

    logger.debug(f'test_api: {case["api"]}')
    logger.debug(f'test_parameter: {case["parameter"]}')

    with allure.step("左臂查询上电状态"):
        l_response = device.ml.is_power_on()
    with allure.step("右臂查询上电状态"):
        r_response = device.mr.is_power_on()

    with allure.step("左臂断言返回类型"):
        assert isinstance(l_response, int), f"左臂返回类型错误：{type(l_response)}"
    with allure.step("右臂断言返回类型"):
        assert isinstance(r_response, int), f"右臂返回类型错误：{type(r_response)}"

    with allure.step("左臂断言返回结果"):
        allure.attach(str(case['l_expect_data']),name= "左臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(l_response),name= "左臂实际值",attachment_type= allure.attachment_type.TEXT)
        assert l_response == case["l_expect_data"], f"左臂结果断言失败，期望：{case['l_expect_data']}，实际：{l_response}"
    with allure.step("右臂断言返回结果"):
        allure.attach(str(case['r_expect_data']),name= "右臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(r_response),name= "右臂实际值",attachment_type= allure.attachment_type.TEXT)
        assert r_response == case["r_expect_data"], f"右臂结果断言失败，期望：{case['r_expect_data']}，实际：{r_response}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("机械臂电源状态查询")
@allure.story("查询下电状态")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_off"], ids=lambda c: c["title"])
def test_power_off(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")

    logger.debug(f'test_api: {case["api"]}')
    logger.debug(f'test_parameter: {case["parameter"]}')

    device.power_off()  # 全部下电

    with allure.step("左臂查询上电状态"):
        l_response = device.ml.is_power_on()
    with allure.step("右臂查询上电状态"):
        r_response = device.mr.is_power_on()

    with allure.step("左臂断言返回类型"):
        assert isinstance(l_response, int), f"左臂返回类型错误：{type(l_response)}"
    with allure.step("右臂断言返回类型"):
        assert isinstance(r_response, int), f"右臂返回类型错误：{type(r_response)}"

    with allure.step("左臂断言返回结果"):
        allure.attach(str(case['l_expect_data']),name='左臂期望值',attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(l_response),name='左臂实际值',attachment_type=allure.attachment_type.TEXT)
        assert l_response == case["l_expect_data"], f"左臂结果断言失败，期望：{case['l_expect_data']}，实际：{l_response}"
    with allure.step("右臂断言返回结果"):
        allure.attach(str(case['r_expect_data']),name='右臂期望值',attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(r_response),name='右臂实际值',attachment_type=allure.attachment_type.TEXT)
        assert r_response == case["r_expect_data"], f"右臂结果断言失败，期望：{case['r_expect_data']}，实际：{r_response}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("机械臂电源状态查询")
@allure.story("查询仅上电状态")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_on_only"], ids=lambda c: c["title"])
def test_power_on_only(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")

    logger.debug(f'test_api: {case["api"]}')
    logger.debug(f'test_parameter: {case["parameter"]}')

    device.power_on_only()  # 仅上电

    with allure.step("左臂查询上电状态"):
        l_response = device.ml.is_power_on()
    with allure.step("右臂查询上电状态"):
        r_response = device.mr.is_power_on()

    with allure.step("左臂断言返回类型"):
        assert isinstance(l_response, int), f"左臂返回类型错误：{type(l_response)}"
    with allure.step("右臂断言返回类型"):
        assert isinstance(r_response, int), f"右臂返回类型错误：{type(r_response)}"

    with allure.step("左臂断言返回结果"):
        allure.attach(str(case['l_expect_data']),name='左臂期望值',attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(l_response),name='左臂实际值',attachment_type=allure.attachment_type.TEXT)
        assert l_response == case["l_expect_data"], f"左臂结果断言失败，期望：{case['l_expect_data']}，实际：{l_response}"
    with allure.step("右臂断言返回结果"):
        allure.attach(str(case['r_expect_data']),name='右臂期望值',attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(r_response),name='右臂实际值',attachment_type=allure.attachment_type.TEXT)
        assert r_response == case["r_expect_data"], f"右臂结果断言失败，期望：{case['r_expect_data']}，实际：{r_response}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("机械臂电源状态查询")
@allure.story("急停异常状态查询")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "emergency"], ids=lambda c: c["title"])
def test_emergency(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")

    logger.debug(f'test_api: {case["api"]}')
    logger.debug(f'test_parameter: {case["parameter"]}')

    input(print("请按下急停，点击回车后继续测试"))
    device.ml.power_on()
    device.mr.power_on()

    with allure.step("左臂查询上电状态"):
        l_response = device.ml.is_power_on()
    with allure.step("右臂查询上电状态"):
        r_response = device.mr.is_power_on()

    input(print("请松开急停，点击回车后继续测试"))

    with allure.step("左臂断言返回结果"):
        allure.attach(str(case['l_expect_data']),name='左臂期望值',attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(l_response),name='左臂实际值',attachment_type=allure.attachment_type.TEXT)
        assert l_response == case["l_expect_data"], f"左臂结果断言失败，期望：{case['l_expect_data']}，实际：{l_response}"
    with allure.step("右臂断言返回结果"):
        allure.attach(str(case['r_expect_data']),name='右臂期望值',attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(r_response),name='右臂实际值',attachment_type=allure.attachment_type.TEXT)
        assert r_response == case["r_expect_data"], f"右臂结果断言失败，期望：{case['r_expect_data']}，实际：{r_response}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")
