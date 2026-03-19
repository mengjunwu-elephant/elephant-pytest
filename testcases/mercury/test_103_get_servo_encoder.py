import pytest
import allure
from common1 import logger, assert_almost_equal
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_servo_encoder")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("获取伺服编码器数值")
@pytest.mark.parametrize("case", cases, ids=lambda c: c['title'])
def test_get_servo_encoder(device, case):
    title = case["title"]
    joint = int(case["joint"])  # 确保 joint 为 int 类型

    with allure.step(f"用例【{title}】开始测试"):
        logger.debug(f"API: {case['api']}")
        logger.debug(f"joint: {joint}")

        response = device.mc.get_servo_encoder(joint)

        with allure.step("断言返回类型为 int"):
            assert isinstance(response, int), f"机械臂返回类型错误，实际为 {type(response)}"

        with allure.step("断言机械臂返回值"):
            assert_almost_equal(response,case['l_expect_data'], tol=2048,name='获取单关编码值'), f"机械臂期望值 {case['l_expect_data']}，实际值 {response}"
        logger.info(f"✅ 用例【{title}】测试成功")
        logger.info(f"》》》用例【{title}】测试完成《《《")
