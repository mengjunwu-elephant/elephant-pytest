import time
import pytest
import allure
from pymycobot.error import MyCobot320DataException
from common1 import logger, assert_almost_equal
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot320Base


# 从 Excel 读取测试数据
cases = get_test_data_from_excel(Mycobot320Base.TEST_DATA_FILE, "send_angle")

normal_cases = [case for case in cases if case.get("test_type") == "normal"]
exception_cases = [case for case in cases if case.get("test_type") == "exception"]
logic_cases = [case for case in cases if case.get("test_type") == "logic"]

@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = Mycobot320Base()
    logger.info("初始化完成，接口测试开始")
    dev.go_zero()
    yield dev
    dev.m.set_fresh_mode(0)
    dev.go_zero()
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置单关节角度运动")
@allure.story("正常用例")
@pytest.mark.parametrize("case", normal_cases, ids=[case["title"] for case in normal_cases])
def test_send_angle1(device, case):
    title = case["title"]
    expected = case["expect_data"]
    joint = case["joint"]
    angle = case["angle"]
    speed = case["speed"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'joint:{case["joint"]}')
    logger.debug(f'angle:{case["angle"]}')
    logger.debug(f'speed:{case["speed"]}')

    device.m.set_fresh_mode(0)

    with allure.step(f"调用 send_angle 接口, joint = {case['joint']}, angle = {case['angle']}, speed = {case['speed']}"):
        set_res = device.m.send_angle(joint, angle, speed)
        time.sleep(0.1)
        while True:
            if device.m.is_moving() == 0:
                break
        time.sleep(1)
        get_res = device.m.get_angles()
        logger.debug(f"set_res返回:{set_res},get_res返回:{get_res[joint-1]}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误,应为{type(expected)},实际为 {type(set_res)}"

    with allure.step("断言设置返回值"):
        allure.attach(str(expected), name="set接口期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="set接口实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {set_res}"

    with allure.step("断言获取返回值"):
        allure.attach(str(angle), name="get接口期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res[joint-1]), name="get接口实际值", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(get_res[joint-1], angle, tol=2) #tol代表允许的误差值

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("设置单关节角度运动  ")
@allure.story("异常用例")
@pytest.mark.parametrize("case", exception_cases, ids=[case["title"] for case in exception_cases])
def test_send_angle2(device, case):
    title = case["title"]
    joint = case["joint"]
    angle = case["angle"]
    speed = case["speed"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'joint:{case["joint"]}')
    logger.debug(f'angle:{case["angle"]}')
    logger.debug(f'speed:{case["speed"]}')

    with pytest.raises(MyCobot320DataException, match=".*"):
        device.m.send_angle(joint, angle, speed)

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("设置单关节角度运动")
@allure.story("正常用例")
@pytest.mark.parametrize("case", logic_cases, ids=[case["title"] for case in logic_cases])
def test_send_angle3(device, case):
    title = case["title"]
    expected = case["expect_data"]
    joint = case["joint"]
    angle = case["angle"]
    speed = case["speed"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'joint:{case["joint"]}')
    logger.debug(f'angle:{case["angle"]}')
    logger.debug(f'speed:{case["speed"]}')

    device.m.set_fresh_mode(1)

    with allure.step(f"调用 send_angle 接口, joint = {case['joint']}, angle = {case['angle']}, speed = {case['speed']}"):
        set_res = device.m.send_angle(joint, angle, speed)
        time.sleep(0.1)
        while True:
            if device.m.is_moving() == 0:
                break
        time.sleep(1)
        get_res = device.m.get_angles()
        logger.debug(f"set_res返回:{set_res},get_res返回:{get_res[joint-1]}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误,应为{type(expected)},实际为 {type(set_res)}"

    with allure.step("断言设置返回值"):
        allure.attach(str(expected), name="set接口期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="set接口实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {set_res}"

    with allure.step("断言获取返回值"):
        allure.attach(str(angle), name="get接口期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res[joint-1]), name="get接口实际值", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(get_res[joint-1], angle, tol=2) #tol代表允许的误差值

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')