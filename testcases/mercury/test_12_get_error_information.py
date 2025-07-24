import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_error_information")

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
def reset_device(device):
    yield
    device.ml.clear_error_information()
    device.mr.clear_error_information()
    device.go_zero()

@allure.feature("获取错误信息")
@allure.story("正常状态下获取错误信息")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_get_error_information(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")

    logger.debug(f'test_api: {case["api"]}')
    logger.debug(f'test_parameter: {case["parameter"]}')

    with allure.step("左臂获取错误信息"):
        l_response = device.ml.get_error_information()
    with allure.step("右臂获取错误信息"):
        r_response = device.mr.get_error_information()

    with allure.step("左臂断言返回类型"):
        assert isinstance(l_response, int), f"左臂返回类型错误：{type(l_response)}"
    with allure.step("右臂断言返回类型"):
        assert isinstance(r_response, int), f"右臂返回类型错误：{type(r_response)}"

    with allure.step("左臂断言返回结果"):
        allure.attach(str(case["l_expect_data"]),name= "左臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(l_response),name= "左臂实际值",attachment_type= allure.attachment_type.TEXT)
        assert l_response == case["l_expect_data"], f"左臂断言失败，期望：{case['l_expect_data']}，实际：{l_response}"
    with allure.step("右臂断言返回结果"):
        allure.attach(str(case["r_expect_data"]),name= "右臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(r_response),name= "右臂实际值",attachment_type= allure.attachment_type.TEXT)
        assert r_response == case["r_expect_data"], f"右臂断言失败，期望：{case['r_expect_data']}，实际：{r_response}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("获取错误信息")
@allure.story("奇异点异常错误信息上报")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_singular_point_error(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")

    logger.debug(f'test_api: {case["api"]}')
    logger.debug(f'test_parameter: {case["parameter"]}')

    with allure.step("机械臂运动至奇异点"):
        device.ml.send_angles([0, 0, 0, -20, 0, 0, 0], device.speed)
        device.mr.send_angles([0, 0, 0, -20, 0, 180, 0], device.speed)
        device.ml.send_coord(3, 300, device.speed)
        device.mr.send_coord(3, 300, device.speed)
        input("请观察机械臂末端是否变蓝，点击回车继续测试")

    with allure.step("左臂获取错误信息"):
        l_response = device.ml.get_error_information()
    with allure.step("右臂获取错误信息"):
        r_response = device.mr.get_error_information()

    with allure.step("左臂断言返回类型"):
        assert isinstance(l_response, int), f"左臂返回类型错误：{type(l_response)}"
    with allure.step("右臂断言返回类型"):
        assert isinstance(r_response, int), f"右臂返回类型错误：{type(r_response)}"

    with allure.step("左臂断言返回结果"):
        allure.attach(str(case["l_expect_data"]),name= "左臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(l_response),name= "左臂实际值",attachment_type= allure.attachment_type.TEXT)
        assert l_response == case["l_expect_data"], f"左臂断言失败，期望：{case['l_expect_data']}，实际：{l_response}"
    with allure.step("右臂断言返回结果"):
        allure.attach(str(case["r_expect_data"]),name= "右臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(r_response),name= "右臂实际值",attachment_type= allure.attachment_type.TEXT)
        assert r_response == case["r_expect_data"], f"右臂断言失败，期望：{case['r_expect_data']}，实际：{r_response}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")
