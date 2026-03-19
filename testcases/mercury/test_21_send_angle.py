import time

import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from common1.assert_utils import assert_almost_equal
from settings import MercuryBase

# 加载 Excel 测试数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "send_angle")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.go_zero()
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@pytest.fixture(autouse=True)
def reset_device(device):
    yield
    device.go_zero()

@allure.feature("单关节角度运动")
@allure.story("机械臂正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_send_angle_normal(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    joint = case["joint"]
    angle = case["angle"]
    speed = case["speed"]
    logger.info(f'发送关节参数{joint}')
    logger.info(f'发送角度参数{angle}')
    logger.info(f'发送速度参数{speed}')

    with allure.step("发送 send_angle 指令到机械臂"):
        response = device.mc.send_angle(joint,angle, speed,_async=True)
        device.wait()
        device.wait()
        logger.info(f"机械臂实际设置返回值：{response}")
        time.sleep(2)

    with allure.step('调用 get_angle 接口'):
        get_res = device.mc.get_angle(joint)
        logger.info(f'机械臂实际读取返回值：{get_res}')

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"机械臂返回类型错误: {type(response)}"

    with allure.step("断言返回值是否匹配预期"):
        allure.attach(str(case["l_expect_data"]), name="机械臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际", attachment_type=allure.attachment_type.TEXT)

        assert_almost_equal(response,case["l_expect_data"],tol=1,name='机械臂全关节运动'), f"机械臂响应不一致，期望: {case['l_expect_data']}，实际: {response}"

    with allure.step('断言 get_angles 接口返回值是否匹配预期'):
        allure.attach(str(angle), name="机械臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="机械臂实际", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(angle), name="机械臂期望", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(get_res,angle,tol=1,name='机械臂全关节运动'), f"机械臂响应不一致，期望: {angle}，实际: {get_res}"

    logger.info(f"✅ 用例【{case['title']}】测试通过")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

@allure.feature("单关节角度运动")
@allure.story("机械臂全关节运动")
@pytest.mark.parametrize(
    "case",
    [c for c in cases if c.get("test_type") in ("left", "right")],
    ids=lambda c: c["title"],
)
def test_send_angle(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    joint = case["joint"]
    angle = case["angle"]
    speed = case["speed"]
    logger.info(f'发送关节参数{joint}')
    logger.info(f'发送角度参数：{angle}')
    logger.info(f'速度参数：{speed}')

    with allure.step("发送 send_angle 指令到机械臂"):
        response = device.mc.send_angle(joint,angle, speed)
        device.wait()
        logger.info(f"机械臂实际设置返回值：{response}")

    with allure.step('调用 get_angles 接口'):
        get_res = device.mc.get_angle(joint)
        logger.info(f'机械臂实际读取返回值：{get_res}')

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"机械臂返回类型错误: {type(response)}"

    with allure.step("断言返回值是否匹配预期"):
        allure.attach(str(case["l_expect_data"]), name="机械臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="机械臂实际", attachment_type=allure.attachment_type.TEXT)
        assert case["l_expect_data"] == response, f"机械臂响应不一致，期望: {case['l_expect_data']}，实际: {response}"

    with allure.step('断言 get_angle 接口返回值是否匹配预期'):
        allure.attach(str(angle), name="机械臂期望", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(get_res), name="机械臂实际", attachment_type=allure.attachment_type.TEXT)
        assert_almost_equal(get_res,angle,tol=1,name='机械臂全关节运动'), f"机械臂响应不一致，期望: {angle}，实际: {get_res}"

    logger.info(f"✅ 用例【{case['title']}】测试通过")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")

@allure.feature("单关节角度运动")
@allure.story("异常角度发送触发异常")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_send_angle_exception(device, case):
    logger.info(f"》》》用例【{case['title']}】开始测试《《《")
    joint = case['joint']
    angle = case["angle"]
    speed = case["speed"]
    logger.info(f'发送角度参数：{angle}')
    logger.info(f'速度参数：{speed}')

    with allure.step("尝试发送非法角度并期望抛出 MercuryDataException"):
        with pytest.raises(MercuryDataException, match=".*") as exc_info:
            device.mc.send_angle(joint, angle, speed)

    logger.info(f"✅ 用例【{case['title']}】触发了预期异常: {exc_info.value}")
    logger.info(f"》》》用例【{case['title']}】测试完成《《《")
