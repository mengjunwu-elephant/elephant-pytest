import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "jog_increment_coord")


@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.ml.power_on()
    dev.mr.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.go_zero()
    dev.mr.power_off()
    dev.ml.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")


@pytest.fixture(autouse=True)
def init_coords_before_each_case(device):
    device.init_coords()
    yield


@allure.feature("机械臂Jog增量坐标接口")
@allure.story("正常增量坐标Jog")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_jog_increment_coord_normal(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"API: {case['api']}, Axis: {case['axis']}, Parameter: {case['parameter']}, Speed: {case['speed']}")

    with allure.step("左臂发送 jog_increment_coord 指令"):
        l_response = device.ml.jog_increment_coord(case["axis"], case["parameter"], case["speed"])

    with allure.step("右臂发送 jog_increment_coord 指令"):
        r_response = device.mr.jog_increment_coord(case["axis"], case["parameter"], case["speed"])

    with allure.step("断言左臂响应类型与值"):
        assert isinstance(l_response, int), f"左臂返回类型应为 int，实际为 {type(l_response)}"
        assert l_response == case["l_expect_data"], f"左臂返回值不符，期望：{case['l_expect_data']}，实际：{l_response}"

    with allure.step("断言右臂响应类型与值"):
        assert isinstance(r_response, int), f"右臂返回类型应为 int，实际为 {type(r_response)}"
        assert r_response == case["r_expect_data"], f"右臂返回值不符，期望：{case['r_expect_data']}，实际：{r_response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("机械臂Jog增量坐标接口")
@allure.story("异常参数测试")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_jog_increment_coord_exception(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试异常场景《《《")
    logger.debug(f"API: {case['api']}, Axis: {case['axis']}, Parameter: {case['parameter']}, Speed: {case['speed']}")

    with allure.step("左臂发送 jog_increment_coord 异常请求，断言抛异常"):
        with pytest.raises(MercuryDataException):
            device.ml.jog_increment_coord(case["axis"], case["parameter"], case["speed"])

    logger.info(f"✅ 用例【{title}】异常场景测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")
