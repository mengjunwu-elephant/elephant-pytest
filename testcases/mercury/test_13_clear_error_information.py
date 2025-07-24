import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 读取测试数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "clear_error_information")

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


@allure.feature("错误信息清除接口")
@allure.story("奇异点错误清除")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal1"], ids=lambda c: c["title"])
def test_clear_error_information_with_error(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")

    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameter: {case['parameter']}")

    with allure.step("使机械臂进入奇异点位置"):
        device.ml.send_angles([0, 0, 0, -20, 0, 0, 0], device.speed)
        device.mr.send_angles([0, 0, 0, -20, 0, 180, 0], device.speed)
        device.ml.send_coord(3, 300, device.speed)
        device.mr.send_coord(3, 300, device.speed)

    with allure.step("清除错误信息"):
        l_response = device.ml.clear_error_information()
        r_response = device.mr.clear_error_information()

    with allure.step("断言返回类型为 int"):
        assert isinstance(l_response, int), f"左臂返回类型错误：{type(l_response)}"
        assert isinstance(r_response, int), f"右臂返回类型错误：{type(r_response)}"

    with allure.step("断言清除结果正确"):
        assert l_response == case["l_expect_data"], f"左臂断言失败，期望：{case['l_expect_data']}，实际：{l_response}"
        assert r_response == case["r_expect_data"], f"右臂断言失败，期望：{case['r_expect_data']}，实际：{r_response}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("错误信息清除接口")
@allure.story("无异常状态清除")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal2"], ids=lambda c: c["title"])
def test_clear_error_information_no_error(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")

    logger.debug(f"test_api: {case['api']}")
    logger.debug(f"test_parameter: {case['parameter']}")

    with allure.step("清除错误信息（当前无异常）"):
        l_response = device.ml.clear_error_information()
        r_response = device.mr.clear_error_information()

    with allure.step("断言返回类型为 int"):
        assert isinstance(l_response, int), f"左臂返回类型错误：{type(l_response)}"
        assert isinstance(r_response, int), f"右臂返回类型错误：{type(r_response)}"

    with allure.step("断言清除结果正确"):
        assert l_response == case["l_expect_data"], f"左臂断言失败，期望：{case['l_expect_data']}，实际：{l_response}"
        assert r_response == case["r_expect_data"], f"右臂断言失败，期望：{case['r_expect_data']}，实际：{r_response}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")
