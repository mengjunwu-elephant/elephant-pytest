import time

import pytest
import allure
from pymycobot.error import MyCobot280DataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from common1.assert_utils import assert_almost_equal
from settings import Mycobot280Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(Mycobot280Base.TEST_DATA_FILE, "send_angles")

@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = Mycobot280Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.default_settings()
    dev.mc.close()
    logger.info("环境清理完成，接口测试结束")

@pytest.fixture(autouse=True)
def go_zero(device):
    device.mc.go_home()
    device.wait()

@allure.feature("设置多关节角度")
@allure.story("正确设置多关节角度")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_send_angles(device, case):
    title = case["title"]
    expected = case["expect_data"]
    angles=eval(case["parameter"])

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'test_angle:{case["parameter"]}')
    logger.debug(f'test_speed:{case["speed"]}')
    logger.debug(f'test_fresh_mode:{case["fresh_mode"]}')

    with allure.step("设置运动模式"):
        device.mc.set_fresh_mode(case["fresh_mode"])
        allure.attach(str(case["fresh_mode"]), name="运动模式", attachment_type=allure.attachment_type.TEXT)

    with allure.step("调用 send_angles 接口"):
        response = device.mc.send_angles(angles,case['speed'])
        device.wait()

    with allure.step("断言返回值类型为 list"):
        assert isinstance(response, int), f"返回类型错误，应为 int，实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {response}"

    with allure.step("调用 get_angles 接口获取当前角度"):
        current_angle = device.mc.get_angles()
        allure.attach(str(current_angle), name="当前角度", attachment_type=allure.attachment_type.TEXT)

    with allure.step("断言是否到达点位"):
        result = device.mc.is_in_position(angles, 0)
        assert result==expected,f"机械臂没有到达点位，目标角度为{angles},实际角度为{current_angle}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("设置多关节角度")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_send_angles_exception(device, case):
    title = case["title"]
    angles = eval(case["parameter"])

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')

    with allure.step("打印测试参数信息"):
        logger.debug(f'test_api: {case["api"]}')
        logger.debug(f'test_angle: {angles}')
        logger.debug(f'test_speed: {case["speed"]}')

    with allure.step(f"调用 {case['api']} 异常场景接口,关节为{angles}, 速度为{case['speed']}"):
        with pytest.raises(MyCobot280DataException, match=".*"):
            device.mc.send_angles(angles, case['speed'])

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{title}】测试完成《《《《《')
