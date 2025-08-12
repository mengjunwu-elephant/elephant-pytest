import time
import pytest
import allure
from pymycobot.error import MyCobot320DataException
from common1 import logger, assert_almost_equal
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot320Base


# 从 Excel 读取测试数据
cases = get_test_data_from_excel(Mycobot320Base.TEST_DATA_FILE, "stop")

normal_cases = [case for case in cases if case.get("test_type") == "normal"]
exception_cases = [case for case in cases if case.get("test_type") == "exception"]

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

@allure.feature("停止机器人运动")
@allure.story("正常用例")
@pytest.mark.parametrize("case", normal_cases, ids=[case["title"] for case in normal_cases])
def test_stop1(device, case):
    ID = case["ID"]
    title = case["title"]
    expected_1 = case["expect_data_1"]
    expected_2 = case["expect_data_2"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step('控制机械臂运动'):
        device.different_modes(ID)

    with allure.step(f"调用 stop 接口"):
        time.sleep(0.5)
        get_res1 = device.m.is_moving()
        set_res = device.m.stop()
        device.wait()
        time.sleep(0.5)
        get_res2 = device.m.is_moving()
        logger.debug(f"set_res返回:{set_res},get_res1返回:{get_res1},get_res2返回:{get_res2}")

    with allure.step("断言返回值类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误,应为{type(expected_1)},实际为 {type(set_res)}"

    with allure.step("断言停止运动前is_moving返回值"):
        allure.attach(str(expected_1), name="get接口期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res1), name="get接口实际值", attachment_type=allure.attachment_type.TEXT)
        assert get_res1 == expected_1, f"用例【{title}】断言失败，期望 {expected_1}，实际 {get_res1}"

    with allure.step("断言停止运动后is_moving返回值"):
        allure.attach(str(expected_2), name="get接口期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res2), name="get接口实际值", attachment_type=allure.attachment_type.TEXT)
        assert get_res2 == expected_2, f"用例【{title}】断言失败，期望 {expected_2}，实际 {get_res2}"

    with allure.step("断言stop返回值"):
        allure.attach(str(expected_1), name="set接口期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="set接口实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected_1, f"用例【{title}】断言失败，期望 {expected_1}，实际 {set_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')


@allure.feature("停止机器人运动")
@allure.story("异常用例")
@pytest.mark.parametrize("case", exception_cases, ids=[case["title"] for case in exception_cases])
def test_stop2(device, case):
    title = case["title"]
    expected_1 = case["expect_data_1"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step('机械臂下电'):
        device.m.power_off()

    with allure.step(f"调用 stop 接口"):
        set_res = device.m.stop()
        logger.debug(f"set_res返回:{set_res}")

    with allure.step('机械臂上电'):
        device.m.power_on()

    with allure.step("断言返回值类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误,应为{type(expected_1)},实际为 {type(set_res)}"

    with allure.step("断言stop返回值"):
        allure.attach(str(expected_1), name="set接口期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="set接口实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected_1, f"用例【{title}】断言失败，期望 {expected_1}，实际 {set_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

