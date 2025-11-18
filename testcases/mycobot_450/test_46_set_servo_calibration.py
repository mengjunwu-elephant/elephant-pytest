import time
import pytest
import allure
from pymycobot.error import MyCobotPro450DataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from common1.assert_utils import assert_almost_equal
from settings import Mycobot450Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(Mycobot450Base.TEST_DATA_FILE, "set_servo_calibration")


@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = Mycobot450Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.default_settings()
    #dev.mc.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置舵机零位")
@allure.story("正确设置舵机零位")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_set_servo_calibration1(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'joint:{case["joint"]}')

    with allure.step("使机械臂运动到零位"):
        device.go_zero()
        device.wait()

    with allure.step(f"调用 {case['api']} 接口"):
        response = device.mc.set_servo_calibration(case["joint"])
        logger.debug(f"接口返回：{response}")

    with allure.step('调用 get_angles 接口'):
        angles = device.mc.get_angles()

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    with allure.step("断言get_angles接口返回结果"):
        allure.attach(str(device.zero_angles), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(angles), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(device.zero_angles, angles, 0.1,'设置舵机零位'), f"用例【{title}】断言失败，期望 {device.zero_angles},实际 {angles}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("设置舵机零位")
@allure.story("超限参数验证")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_servo_calibration_exception(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'joint:{case["joint"]}')

    with allure.step(f"断言抛出 Mycobot450Exception,关节为{case['joint']}"):
        with pytest.raises(MyCobotPro450DataException):
            device.mc.set_servo_calibration(case['joint'])

    logger.info(f"✅ 用例【{title}】异常断言通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")
