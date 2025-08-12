import time
import pytest
import allure
from pymycobot.error import MyCobot320DataException
from common1 import logger, assert_almost_equal
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot320Base


# 从 Excel 读取测试数据
cases = get_test_data_from_excel(Mycobot320Base.TEST_DATA_FILE, "is_moving")

normal_cases = [case for case in cases if case.get("test_type") == "normal"]
logic_cases = [case for case in cases if case.get("test_type") == "logic"]
exception_cases_1 = [case for case in cases if case.get("test_type") == "exception_1"]
exception_cases_2 = [case for case in cases if case.get("test_type") == "exception_2"]

@pytest.fixture(scope="module")
def device():
    """设备初始化和清理"""
    dev = Mycobot320Base()
    logger.info("初始化完成，接口测试开始")
    dev.go_zero()
    yield dev
    dev.go_zero()
    dev.m.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("判断是否在某个位置")
@allure.story("正常用例")
@pytest.mark.parametrize("case", normal_cases, ids=[case["title"] for case in normal_cases])
def test_is_moving1(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step('控制机械臂角度运动'):
        device.go_zero()
        device.m.send_angles(device.angles_init, device.speed)
        time.sleep(0.3)

    with allure.step(f"调用 is_moving 接口"):
        get_res = device.m.is_moving()
        logger.debug(f"get_res返回:{get_res}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(get_res, int), f"返回类型错误,应为{type(expected)},实际为 {type(get_res)}"

    with allure.step("断言is_paused返回值"):
        allure.attach(str(expected), name="get接口期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="get接口实际值", attachment_type=allure.attachment_type.TEXT)
        assert get_res == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {get_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')


@allure.feature("判断是否在某个位置")
@allure.story("正常用例")
@pytest.mark.parametrize("case", logic_cases, ids=[case["title"] for case in logic_cases])
def test_is_moving2(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step('控制机械臂角度运动'):
        device.go_coords()
        device.m.send_coords([260, -89.4, 235.9, 178.24, 0.18, -90.0], device.speed)
        time.sleep(0.3)

    with allure.step(f"调用 is_moving 接口"):
        get_res = device.m.is_moving()
        logger.debug(f"get_res返回:{get_res}")
        time.sleep(5)

    with allure.step("断言返回值类型为 int"):
        assert isinstance(get_res, int), f"返回类型错误,应为{type(expected)},实际为 {type(get_res)}"

    with allure.step("断言is_paused返回值"):
        allure.attach(str(expected), name="get接口期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="get接口实际值", attachment_type=allure.attachment_type.TEXT)
        assert get_res == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {get_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("判断是否在某个位置")
@allure.story("正常用例")
@pytest.mark.parametrize("case", exception_cases_1, ids=[case["title"] for case in exception_cases_1])
def test_is_moving3(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step(f"调用 is_moving 接口"):
        get_res = device.m.is_moving()
        logger.debug(f"get_res返回:{get_res}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(get_res, int), f"返回类型错误,应为{type(expected)},实际为 {type(get_res)}"

    with allure.step("断言is_paused返回值"):
        allure.attach(str(expected), name="get接口期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="get接口实际值", attachment_type=allure.attachment_type.TEXT)
        assert get_res == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {get_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')


@allure.feature("恢复机器人运动并完成上一个命令")
@allure.story("异常用例")
@pytest.mark.parametrize("case", exception_cases_2, ids=[case["title"] for case in exception_cases_2])
def test_is_moving4(device, case):
    ID = case["ID"]
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step('机械臂下电'):
        device.m.power_off()

    with allure.step(f"调用 is_moving 接口"):
        set_res = device.m.is_moving()
        logger.debug(f"set_res返回:{set_res}")

    with allure.step('机械臂上电'):
        device.m.power_on()

    with allure.step("断言返回值类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误,应为{type(expected)},实际为 {type(set_res)}"

    with allure.step("断言is_moving返回值"):
        allure.attach(str(expected), name="set接口期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="set接口实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {set_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')



