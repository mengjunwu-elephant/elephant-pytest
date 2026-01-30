import time
import pytest
import allure
from pymycobot.error import MercuryE1DataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from common1.assert_utils import assert_almost_equal
from settings import MercuryE1Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(MercuryE1Base.TEST_DATA_FILE, "set_joint_max_angle")


@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = MercuryE1Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.default_angle()
    dev.mc.close()
    logger.info("环境清理完成，接口测试结束")

@pytest.fixture(autouse=True)
def reset_device(device):
    yield
    device.go_zero()
    device.wait()

@allure.feature("设置关节最大角度")
@allure.story("正确设置关节最大角度")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_set_joint_max_angle1(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step(f"调用 {case['api']} 接口"):
        response = device.mc.set_joint_max_angle(case["joint"],case["angle"])
        logger.debug(f"接口返回：{response}")

    with allure.step('调整3关节角度，放置碰撞'):
        if case["joint"] == 2:
            device.mc.send_angle(3, -90,device.speed)
            device.wait()

    with allure.step('调用 send_angle 接口,使机械臂运动到最大角度范围外'):
        device.mc.send_angle(case["joint"],case["angle"]+5,device.speed)
        device.wait()

    with allure.step('调用 get_angles 接口,获取当前角度'):
        angle = device.mc.get_angle(case['joint'])
        logger.debug(f"当前角度：{angle}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    with allure.step("断言get_angle接口返回结果"):
        allure.attach(str(case['angle']), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(angle), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(angle, case['angle'], 1,'设置关节最大角度'), f"用例【{title}】断言失败，期望 {case['angle']},实际 {angle}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("设置关节最大角度")
@allure.story("超限参数验证")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_joint_max_angle_exception(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'joint:{case["joint"]}')

    with allure.step(f"断言抛出 MercuryE1DataException,关节为{case['joint']},角度为{case['angle']}"):
        with pytest.raises(MercuryE1DataException):
            device.mc.set_joint_max_angle(case['joint'],case['angle'])

    logger.info(f"✅ 用例【{title}】异常断言通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")
