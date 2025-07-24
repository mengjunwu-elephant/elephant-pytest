import pytest
import allure
from pymycobot.error import MercuryDataException
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "jog_increment_angle")


@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.ml.power_on()
    dev.mr.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.go_zero()
    dev.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")


@pytest.fixture(autouse=True)
def teardown_go_zero(device):
    yield
    device.go_zero()


@allure.feature("机械臂Jog增量角度接口")
@allure.story("正常增量角度Jog")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_jog_increment_angle_left(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试（左臂）《《《")
    logger.debug(f"API: {case['api']}, Joint: {case['joint']}, Parameter: {case['parameter']}, Speed: {case['speed']}")

    with allure.step("调用左臂 jog_increment_angle 接口"):
        l_response = device.ml.jog_increment_angle(case["joint"], case["parameter"], case["speed"])

    with allure.step("断言返回类型和返回值"):
        assert isinstance(l_response, int), f"左臂返回类型应为 int，实际为 {type(l_response)}"
        assert l_response == case["l_expect_data"], f"左臂返回值不符，期望：{case['l_expect_data']}，实际：{l_response}"

    logger.info(f"✅ 用例【{title}】左臂测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("机械臂Jog增量角度接口")
@allure.story("正常增量角度Jog")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_jog_increment_angle_right(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试（右臂）《《《")
    logger.debug(f"API: {case['api']}, Joint: {case['joint']}, Parameter: {case['parameter']}, Speed: {case['speed']}")

    with allure.step("调用右臂 jog_increment_angle 接口"):
        r_response = device.mr.jog_increment_angle(case["joint"], case["parameter"], case["speed"])

    with allure.step("断言返回类型和返回值"):
        assert isinstance(r_response, int), f"右臂返回类型应为 int，实际为 {type(r_response)}"
        assert r_response == case["r_expect_data"], f"右臂返回值不符，期望：{case['r_expect_data']}，实际：{r_response}"

    logger.info(f"✅ 用例【{title}】右臂测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("机械臂Jog增量角度接口")
@allure.story("异常参数测试")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_jog_increment_angle_out_limit(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试（异常场景）《《《")
    logger.debug(f"API: {case['api']}, Joint: {case['joint']}, Parameter: {case['parameter']}, Speed: {case['speed']}")

    with allure.step("调用左臂 jog_increment_angle 异常接口"):
        with pytest.raises(MercuryDataException):
            device.ml.jog_increment_angle(case["joint"], case["parameter"], case["speed"])

    with allure.step("调用右臂 jog_increment_angle 异常接口"):
        with pytest.raises(MercuryDataException):
            device.mr.jog_increment_angle(case["joint"], case["parameter"], case["speed"])

    logger.info(f"✅ 用例【{title}】异常场景测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")
