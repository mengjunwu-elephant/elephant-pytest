import pytest
import allure
from common1 import logger, assert_almost_equal
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase
from pymycobot.error import MercuryDataException

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_servo_encoder")


@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.ml.power_on()
    dev.mr.power_on()
    logger.info("初始化完成，接口测试开始")
    dev.go_zero()
    yield dev
    dev.mr.power_off()
    dev.ml.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("获取伺服编码器数值")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_get_servo_encoder(device, case):
    title = case["title"]
    joint = int(case["joint"])  # 确保 joint 为 int 类型

    with allure.step(f"用例【{title}】开始测试"):
        logger.debug(f"API: {case['api']}")
        logger.debug(f"joint: {joint}")

        l_response = device.ml.get_servo_encoder(joint)
        r_response = device.mr.get_servo_encoder(joint)

        with allure.step("断言返回类型为 int"):
            assert isinstance(l_response, int), f"左臂返回类型错误，实际为 {type(l_response)}"
            assert isinstance(r_response, int), f"右臂返回类型错误，实际为 {type(r_response)}"

        with allure.step("断言左臂返回值"):
            assert_almost_equal(l_response,case['l_expect_data'], tol=2048,name='获取单关编码值'), f"左臂期望值 {case['l_expect_data']}，实际值 {l_response}"

        with allure.step("断言右臂返回值"):
            assert_almost_equal(r_response,case['r_expect_data'], tol=2048,name='获取单关编码值'), f"右臂期望值 {case['r_expect_data']}，实际值 {r_response}"

        logger.info(f"✅ 用例【{title}】测试成功")
        logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("获取伺服编码器数值")
@allure.story("获取伺服编码器数值-关节超限")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_get_angle_invalid(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")

    joint = case["joint"]

    with allure.step("断言非法 joint 索引抛出 MercuryDataException"):
        with pytest.raises(MercuryDataException, match=".*") as exc_info:
            device.ml.get_angle(joint)
            device.mr.get_angle(joint)

    allure.attach(str(joint), name="非法关节索引", attachment_type=allure.attachment_type.TEXT)

    logger.info(f"✅ 用例【{case['title']}】触发了预期异常: {exc_info.value}")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")
