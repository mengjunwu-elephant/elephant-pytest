import time
from time import sleep

import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MyAGVProBase

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(MyAGVProBase.TEST_DATA_FILE, "set_led_mode")

@pytest.fixture(autouse=True)
def reset(device):
    # 每个用例后设置两侧灯带为初始状态
    yield
    device.set_led_color_reset()

@allure.feature("设置灯带模式")
@allure.story("设置灯带模式（上电）")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal1"], ids=lambda c: c["title"])
def test_set_led_mode1(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("小车上电"):
        device.mc.power_on()

    with allure.step("调用 set_led_mode 接口"):
        response = device.mc.set_led_mode(case['mode'])
        logger.debug(f"设置接口返回：{response}")

    with allure.step("调用 set_led_color 接口"):
        device.mc.set_led_color(0,(255,0,0),100)

    res = input(f"灯带是否设置红色失败, 失败回车, 成功输入1")

    with allure.step("断言灯带是否设置红色失败"):
        assert res != '1', f"灯带设置红色成功, 期望 '', 实际 {res}"

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言设置接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("设置灯带模式")
@allure.story("设置灯带模式（上电）")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal2"], ids=lambda c: c["title"])
def test_set_led_mode2(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("小车上电"):
        device.mc.power_on()

    with allure.step("调用 set_led_mode 接口"):
        response = device.mc.set_led_mode(case['mode'])
        logger.debug(f"设置接口返回：{response}")

    with allure.step("调用 set_led_color 接口"):
        device.mc.set_led_color(0,(255,0,0),100)

    res = input(f"灯带是否设置红色成功, 成功回车, 失败输入1")

    with allure.step("断言灯带是否设置成功"):
        assert res != '1', f"灯带设置红色失败, 期望 '', 实际 {res}"

    with allure.step("小车重启, 重置灯带颜色"):
        device.reset()
        device.set_led_color_reset()

    with allure.step("调用 set_led_color 接口"):
        device.mc.set_led_color(0,(255,0,0),100)

    res = input(f"灯带是否设置红色失败, 失败回车, 成功输入1")

    with allure.step("断言灯带是否设置红色失败"):
        assert res != '1', f"灯带设置红色成功, 期望 '', 实际 {res}"

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言设置接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("设置灯带模式")
@allure.story("设置灯带模式（下电）")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "power_off"], ids=lambda c: c["title"])
def test_set_led_mode3(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("小车下电"):
        device.mc.power_off()

    with allure.step("调用 set_led_mode 接口"):
        response = device.mc.set_led_mode(case['mode'])
        logger.debug(f"接口返回：{response}")

    with allure.step("小车上电"):
        device.mc.power_on()

    with allure.step("断言返回值类型"):
        assert response is None, f"机械臂返回类型错误，期望None，实际{type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("设置灯带模式")
@allure.story("设置灯带模式（参数超限）")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_led_mode4(device, case):
    title = case["title"]

    if '参数类型超限' in title:
        mode = eval(case['mode'])
    else:
        mode = case['mode']

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step(f"断言抛出 ValueError"):
        with pytest.raises(ValueError):
            device.mc.set_led_mode(mode)

    logger.info(f"✅ 用例【{title}】异常断言通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")
