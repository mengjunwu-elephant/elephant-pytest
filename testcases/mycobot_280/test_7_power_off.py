import time

import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot280Base

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(Mycobot280Base.TEST_DATA_FILE, "power_off")

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
    yield
    device.mc.send_angles(device.init_angles, device.speed)
    device.wait()

@allure.feature("机械臂上电")
@allure.story("机械臂下电情况下电")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_off"], ids=lambda c: c["title"])
def test_power_off(device, case):
    title = case["title"]
    expected = case["expect_data"]
    is_power_on_status = case["is_power_on_status"]
    move_status = case['move_status']

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'test_expected:{expected}')
    logger.debug(f'test_is_power_on_status:{is_power_on_status}')
    logger.debug(f'move_status:{move_status}')

    with allure.step("调用 power_off 接口"):
        device.mc.power_off()

    with allure.step("测试power_off状态下进行下电的返回值"):
        response = device.mc.power_off()
        logger.debug(f"接口返回：{response}")

    with allure.step('调用is_power_on 接口'):
        get_res = device.mc.is_power_on()

    with allure.step('调用send_angles 接口，查看是否能够运动'):
        move_res = device.mc.send_angles(device.coords_init_angles,device.speed)
        device.wait()

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response,int), f"返回类型错误，应为 int，实际为 {type(response)}"

    with allure.step("断言接口返回结果，is_power_on状态"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {response}"
        assert get_res == is_power_on_status, f"用例【{title}】断言失败，期望 {is_power_on_status}，实际 {get_res}"
        assert move_res == move_status, f"用例【{title}】断言失败，期望 {move_status}，实际 {move_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')


@allure.feature("机械臂上电")
@allure.story("机械臂上电情况下电")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_on"], ids=lambda c: c["title"])
def test_power_on(device, case):
    title = case["title"]
    expected = case["expect_data"]
    is_power_on_status = case["is_power_on_status"]
    move_status = case['move_status']

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')
    logger.debug(f'test_expected:{expected}')
    logger.debug(f'test_is_power_on_status:{is_power_on_status}')
    logger.debug(f'move_status:{move_status}')

    with allure.step("调用 power_on 接口"):
        device.mc.power_on()

    with allure.step("调用 power_off 接口"):
        response = device.mc.power_off()
        logger.debug(f"接口返回：{response}")

    with allure.step('调用is_power_on 接口'):
        get_res = device.mc.is_power_on()

    with allure.step('调用send_angles 接口，查看是否能够运动'):
        move_res = device.mc.send_angles(device.coords_init_angles,device.speed)
        device.wait()

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误，应为 int，实际为 {type(response)}"

    with allure.step("断言接口返回结果，is_power_on状态"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected}，实际 {response}"
        assert get_res == is_power_on_status, f"用例【{title}】断言失败，期望 {is_power_on_status}，实际 {get_res}"
        assert move_res == move_status, f"用例【{title}】断言失败，期望 {move_status}，实际 {move_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')