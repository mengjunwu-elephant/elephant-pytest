import time
import pytest
import allure
from pymycobot.error import MyCobot320DataException
from common1 import logger, assert_almost_equal
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot320Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(Mycobot320Base.TEST_DATA_FILE, "joint_brake")

normal_cases = [case for case in cases if case.get("test_type") == "normal"]
exception_cases = [case for case in cases if case.get("test_type") == "exception"]


@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = Mycobot320Base()
    logger.info("初始化完成，接口测试开始")
    dev.go_zero()
    dev.m.set_fresh_mode(1)
    yield dev
    dev.m.set_fresh_mode(0)
    dev.go_zero()
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置指定关节停止运动")
@allure.story("正常用例")
@pytest.mark.parametrize("case", normal_cases, ids=[case["title"] for case in normal_cases])
def test_joint_brake1(device, case):
    title = case["title"]
    expected_1 = case["expect_data_1"]
    expected_2 = case["expect_data_2"]
    joint = case["joint"]
    speed = case["speed"]
    target_anlge = case["target_anlge"]
    stop_angle = case["stop_angle"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'test_id:{case["joint"]}')
    logger.debug(f'test_speed:{case["speed"]}')

    with allure.step('机械臂运动对应关节'):
        device.m.send_angle(joint, target_anlge, speed)

    with allure.step("调用 joint_brake 接口"):
        while 1:
            angle = device.m.get_angles()
            if angle[joint - 1] >= int(stop_angle) :
                set_res = device.m.joint_brake(joint)
                break
        time.sleep(2)
        get_res = device.m.get_angles()
        logger.debug(f"set_res返回:{set_res},get_res返回:{get_res[joint-1]}")

    with allure.step('将机械臂运动到对应关节0'):
        device.m.send_angle(joint, 0, device.speed)
        device.wait()

    with allure.step("断言返回值类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误,应为{type(expected_1)},实际为 {type(set_res)}"

    with allure.step("断言 joint_brake 返回结果"):
        allure.attach(str(expected_1), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected_1, f"用例【{title}】断言失败，期望 {expected_1}，实际 {set_res}"

    with allure.step("断言 get_angles 返回结果"):
        allure.attach(str(stop_angle), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res[joint-1]), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(get_res[joint-1], stop_angle, tol=expected_2) #tol代表允许的误差值

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')


@allure.feature("设置指定关节停止运动超限")
@allure.story("异常用例")
@pytest.mark.parametrize("case", exception_cases, ids=[case["title"] for case in exception_cases])
def test_joint_brake2(device, case):
    title = case["title"]
    joint = case["joint"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'test_id:{case["joint"]}')

    with pytest.raises(MyCobot320DataException, match=".*"):
        device.m.joint_brake(joint)

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')