import time
from time import sleep

import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MyAGVProBase

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(MyAGVProBase.TEST_DATA_FILE, "set_led_color")

@pytest.fixture(autouse=True)
def reset(device):
    # 每个用例后设置两侧灯带为初始状态
    yield
    device.set_led_color_reset()

@allure.feature("DIY灯带")
@allure.story("DIY灯带（上电）")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_set_led_color1(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("小车上电"):
        device.mc.power_on()

    with allure.step("设置灯带模式DIY"):
        device.mc.set_led_mode(1)

    with allure.step("调用 set_led_color 接口"):
        response = device.mc.set_led_color(case['position'], eval(case['color']), case['brightness'])
        logger.debug(f"设置接口返回：{response}")

    res = input(f"初始状态, 两侧灯带绿色亮度85\n"
                f"{title}, 查看灯带是否设置成功, 正确回车, 错误输入1\n")

    with allure.step("断言灯带是否设置成功"):
        assert res != '1', f"灯带设置失败, 期望 '', 实际 {res}"

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言设置接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')


@allure.feature("DIY灯带")
@allure.story("DIY灯带（下电）")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "power_off"], ids=lambda c: c["title"])
def test_set_led_color2(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("小车下电"):
        device.mc.power_off()

    with allure.step("调用 set_led_color 接口"):
        response = device.mc.set_led_color(case['position'], eval(case['color']), case['brightness'])
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

@allure.feature("DIY灯带")
@allure.story("DIY灯带（参数超限）")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception1"], ids=lambda c: c["title"])
def test_set_led_color3(device, case):
    title = case["title"]

    if '参数类型超限' in title:
        position = eval(case['position'])
    else:
        position = case['position']

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step(f"断言抛出 ValueError"):
        with pytest.raises(ValueError):
            device.mc.set_led_color(position, eval(case['color']), case['brightness'])

    logger.info(f"✅ 用例【{title}】异常断言通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("DIY灯带")
@allure.story("DIY灯带（参数超限）")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception2"], ids=lambda c: c["title"])
def test_set_led_color4(device, case):
    title = case["title"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step(f"断言抛出 ValueError"):
        with pytest.raises(ValueError):
            device.mc.set_led_color(case['position'], eval(case['color']), case['brightness'])

    logger.info(f"✅ 用例【{title}】异常断言通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("DIY灯带")
@allure.story("DIY灯带（参数超限）")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception3"], ids=lambda c: c["title"])
def test_set_led_color5(device, case):
    title = case["title"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    if '参数类型超限' in title:
        brightness = eval(case['brightness'])
        with allure.step(f"断言抛出 TypeError"):
            with pytest.raises(TypeError):
                device.mc.set_led_color(case['position'], eval(case['color']), brightness)
    else:
        brightness = case['brightness']
        with allure.step(f"断言抛出 ValueError"):
            with pytest.raises(ValueError):
                device.mc.set_led_color(case['position'], eval(case['color']), brightness)



    logger.info(f"✅ 用例【{title}】异常断言通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")
