import time
import pytest
import allure
from pymycobot.error import MyCobotPro450DataException

from common1 import logger, assert_almost_equal
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot450Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(Mycobot450Base.TEST_DATA_FILE, "solve_inv_kinematics")


@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = Mycobot450Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.go_zero()
    dev.mc.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("计算运动学逆解")
@allure.story("正确计算运动学逆解")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_solve_inv_kinematics1(device, case):
    title = case["title"]
    expected = eval(case["expect_data"])
    target_coords = eval(case["target_coords"])
    current_angles = eval(case["current_angles"])

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'test_target_coords:{target_coords}')
    logger.debug(f'test_current_angles:{current_angles}')

    with allure.step(f"调用 {case['api']} 接口"):
        set_res = device.mc.solve_inv_kinematics(target_coords, current_angles)
        time.sleep(1)
        logger.debug(f"接口返回：{set_res}")

    with allure.step('使机械臂运动到逆解计算位置,并获取坐标，是否为目标坐标'):
        device.mc.send_angles(set_res,device.speed)
        device.wait()
        coords = device.mc.get_coords()

    with allure.step("断言返回值类型为 list"):
        assert isinstance(set_res, list), f"返回类型错误,应为{type(expected)},实际为 {type(set_res)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected, f"用例【{title}】断言失败，期望 {expected},实际 {set_res}"

    with allure.step("断言机械臂坐标是否为目标坐标"):
        allure.attach(str(target_coords), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(coords), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(coords,target_coords,tol=3,name='计算运动学逆解'), f"用例【{title}】断言失败，期望 {target_coords},实际 {coords}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("计算运动学逆解")
@allure.story("计算运动学逆解无解")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "logic"], ids=lambda c: c["title"])
def test_solve_inv_kinematics2(device, case):
    title = case["title"]
    expected = case["expect_data"]
    target_coords = eval(case["target_coords"])
    current_angles = eval(case["current_angles"])

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'test_target_coords:{target_coords}')
    logger.debug(f'test_current_angles:{current_angles}')

    with allure.step(f"调用 {case['api']} 接口"):
        set_res = device.mc.solve_inv_kinematics(target_coords, current_angles)
        time.sleep(1)
        logger.debug(f"接口返回：{set_res}")

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected, f"用例【{title}】断言失败，期望 {expected},实际 {set_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("计算运动学逆解")
@allure.story("超限参数验证")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_solve_inv_kinematics_exception(device, case):
    title = case["title"]
    expected = case["expect_data"]
    target_coords = eval(case["target_coords"])
    current_angles = eval(case["current_angles"])

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'test_target_coords:{target_coords}')
    logger.debug(f'test_current_angles:{current_angles}')

    with allure.step(f"断言抛出 Mycobot450Exception,目标坐标为{target_coords}，当前角度为{current_angles}"):
        with pytest.raises(MyCobotPro450DataException) as exc:
            device.mc.solve_inv_kinematics(target_coords, current_angles)

    logger.info(f"✅ 用例【{title}】异常断言通过,异常信息：{exc.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")
