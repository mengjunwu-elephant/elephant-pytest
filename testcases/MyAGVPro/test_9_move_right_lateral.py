import time
import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MyAGVProBase

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(MyAGVProBase.TEST_DATA_FILE, "move_right_lateral")


@allure.feature("小车向右平移")
@allure.story("小车向右平移（上电）")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "power_on"], ids=lambda c: c["title"])
def test_move_right_lateral1(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("小车上电"):
        device.mc.power_on()

    with allure.step("调用 move_right_lateral 接口"):
        response = device.mc.move_right_lateral(case['parameters'])
        logger.debug(f"接口返回：{response}")

    res = input(f'查看小车是否向右平移运动, 是回车, 不是输入1\n')
    with allure.step("断言小车运动方向是否正确"):
        assert res != '1', f"小车运动方向错误, 期望 '' ,实际 1"

    with allure.step("小车停止运动"):
        device.mc.stop()

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')


@allure.feature("小车向右平移")
@allure.story("小车向右平移（下电）")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "power_off"], ids=lambda c: c["title"])
def test_move_right_lateral2(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("小车下电"):
        device.mc.power_off()

    with allure.step("调用 move_right_lateral 接口"):
        response = device.mc.move_right_lateral(case['parameters'])
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

@allure.feature("小车向右平移")
@allure.story("小车向右平移（参数超限）")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_move_right_lateral3(device, case):
    title = case["title"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    if '参数类型超限' in title:
        parameters = eval(case['parameters'])
        with allure.step(f"断言抛出 TypeError,模式为{parameters}"):
            with pytest.raises(TypeError):
                device.mc.move_forward(parameters)
    else:
        with allure.step(f"断言抛出 ValueError,模式为{case['parameters']}"):
            with pytest.raises(ValueError):
                device.mc.move_forward(case['parameters'])

    logger.info(f"✅ 用例【{title}】异常断言通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")
