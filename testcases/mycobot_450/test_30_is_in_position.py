import time

import pytest
import allure
from pymycobot.error import MercuryDataException, MyCobotPro450DataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot450Base

# 从Excel中提取数据
cases = get_test_data_from_excel(Mycobot450Base.TEST_DATA_FILE, "is_in_position")


@pytest.fixture(scope="module")
def device():
    dev = Mycobot450Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.default_settings()
    dev.go_zero()
    time.sleep(8)
    logger.info("环境清理完成，接口测试结束")


@allure.feature("是否到达指定点位")
@allure.story("角度判断")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == 'angles'], ids=lambda c: c["title"])
def test_is_in_position_angles(device, case):
    title = case["title"]
    param = case["parameter"]
    mode = case["mode"]
    expected = case["expect_data"]

    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"接口: {case['api']}，参数: {param}，模式: {mode}")

    with allure.step('使机械臂运动'):
        device.mc.send_angles(device.coords_init_angles,device.speed)
        device.wait()

    with allure.step(f"调用 {case['api']} 接口查看角度是否在点位"):
        response = device.mc.is_in_position(eval(param), mode)

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("是否到达指定点位")
@allure.story("坐标判断")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == 'coords'], ids=lambda c: c["title"])
def test_is_in_position_coords(device, case):
    title = case["title"]
    param = case["parameter"]
    mode = case["mode"]
    expected = case["expect_data"]

    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"接口: {case['api']}，参数: {param}，模式: {mode}")

    with allure.step('使机械臂运动'):
        device.mc.send_angles(device.coords_init_angles, device.speed)
        device.wait()

    with allure.step(f"调用 {case['api']} 接口查看坐标是否在点位"):
        response = device.mc.is_in_position(eval(param), mode)

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("是否到达指定点位")
@allure.story("异常参数测试")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "exception"], ids=lambda c: c["title"])
def test_is_in_position_exception(device, case):
    title = case["title"]
    param = case["parameter"]
    mode = case["mode"]

    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"接口: {case['api']}，参数: {param}，模式: {mode}")

    with allure.step("断言抛出 MyCobotPro450DataException"):
        with pytest.raises(MyCobotPro450DataException):
            device.mc.is_in_position(param, mode)

    logger.info(f"✅ 用例【{title}】异常测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")