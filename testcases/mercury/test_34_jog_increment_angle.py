import pytest
import allure
from pymycobot.error import MercuryDataException
from common1 import logger, assert_almost_equal
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "jog_increment_angle")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
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
def test_jog_increment_angle(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试（机械臂）《《《")
    logger.debug(f"API: {case['api']}, Joint: {case['joint']}, Parameter: {case['parameter']}, Speed: {case['speed']}")

    with allure.step("调用机械臂 jog_increment_angle 接口"):
        response = device.mc.jog_increment_angle(case["joint"], case["parameter"], case["speed"])
        device.wait()

    with allure.step("调用get_angle接口"):
        get_res = device.mc.get_angle(case["joint"])
        logger.info(f"机械臂get_angle接口返回值：{get_res}")

    with allure.step("断言返回类型"):
        assert isinstance(response, int), f"机械臂返回类型应为 int，实际为 {type(response)}"

    with allure.step("断言返回值"):
        allure.attach(str(case["l_expect_data"]), name="机械臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际", attachment_type=allure.attachment_type.TEXT)
        assert response == case["l_expect_data"], f"机械臂返回值不符，期望：{case['l_expect_data']}，实际：{response}"

    with allure.step("断言get_angle接口返回值"):
        allure.attach(str(device.init_angles[case['joint']-1]+case["parameter"]), name="机械臂get_angle期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="机械臂get_angle实际", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(get_res,device.init_angles[case['joint']-1]+case["parameter"], 1), f"机械臂期望：{device.init_angles[case['joint']-1]+case['parameter']}，实际：{get_res}"

    logger.info(f"✅ 用例【{title}】机械臂测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("机械臂Jog增量角度接口")
@allure.story("异常参数测试")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_jog_increment_angle_out_limit(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试（异常场景）《《《")
    logger.debug(f"API: {case['api']}, Joint: {case['joint']}, Parameter: {case['parameter']}, Speed: {case['speed']}")

    with allure.step("调用机械臂 jog_increment_angle 异常接口"):
        with pytest.raises(MercuryDataException) as exc_info:
            device.mc.jog_increment_angle(case["joint"], case["parameter"], case["speed"])

    logger.info(f"✅ 用例【{case['title']}】触发了预期异常: {exc_info.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")
