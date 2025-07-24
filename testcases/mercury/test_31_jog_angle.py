import pytest
import allure
from time import sleep

from pymycobot.error import MercuryDataException
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "jog_angle")


@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.ml.power_on()
    dev.mr.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.go_zero()
    dev.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")


@pytest.fixture(autouse=True)
def reset_arm(device):
    yield
    device.go_zero()


@allure.feature("jog_angle 接口测试")
@allure.story("正常用例 - 左臂")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_jog_angle_left(device, case):
    joint = case["joint"]
    param = case["parameter"]
    speed = case["speed"]
    title = case["title"]

    logger.info(f"》》》开始用例【{title}】《《《")
    logger.debug(f"joint={joint}, param={param}, speed={speed}")

    with allure.step("发送 jog_angle 指令（左臂）"):
        response = device.ml.jog_angle(joint, param, speed)
        sleep(2)

    with allure.step("判断是否到达软件限位（左臂）"):
        current_angle = device.ml.get_angle(joint)
        target = device.min_limit[joint - 1] if param == 0 else device.max_limit[joint - 1]
        reached = device.is_in_position(target, current_angle)
        assert reached == 1, f"左臂 {joint} 号关节未到达限位, 当前角度: {current_angle}"

    with allure.step("断言响应结果正确（左臂）"):
        assert isinstance(response, int), f"返回值类型错误: {type(response)}"
        assert response == case["l_expect_data"], f"期望值: {case['l_expect_data']}, 实际值: {response}"

    logger.info(f"✅ 用例【{title}】测试成功")


@allure.feature("jog_angle 接口测试")
@allure.story("正常用例 - 右臂")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_jog_angle_right(device, case):
    joint = case["joint"]
    param = case["parameter"]
    speed = case["speed"]
    title = case["title"]

    logger.info(f"》》》开始用例【{title}】《《《")
    logger.debug(f"joint={joint}, param={param}, speed={speed}")

    with allure.step("发送 jog_angle 指令（右臂）"):
        response = device.mr.jog_angle(joint, param, speed)
        sleep(2)

    with allure.step("判断是否到达软件限位（右臂）"):
        current_angle = device.mr.get_angle(joint)
        target = device.min_limit[joint - 1] if param == 0 else device.max_limit[joint - 1]
        reached = device.is_in_position(target, current_angle)
        assert reached == 1, f"右臂 {joint} 号关节未到达限位, 当前角度: {current_angle}"

    with allure.step("断言响应结果正确（右臂）"):
        assert isinstance(response, int), f"返回值类型错误: {type(response)}"
        assert response == case["r_expect_data"], f"期望值: {case['r_expect_data']}, 实际值: {response}"

    logger.info(f"✅ 用例【{title}】测试成功")


@allure.feature("jog_angle 接口测试")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "exception"], ids=lambda c: c["title"])
def test_jog_angle_exception(device, case):
    joint = case["joint"]
    param = case["parameter"]
    speed = case["speed"]
    title = case["title"]

    logger.info(f"》》》开始异常用例【{title}】《《《")
    logger.debug(f"joint={joint}, param={param}, speed={speed}")

    with allure.step("发送非法 jog_angle 指令，期待触发 MercuryDataException"):
        with pytest.raises(MercuryDataException):
            device.ml.jog_angle(joint, param, speed)
            device.mr.jog_angle(joint, param, speed)

    logger.info(f"✅ 异常用例【{title}】触发成功")
