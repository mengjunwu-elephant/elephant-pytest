import time
import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MyAGVProBase

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(MyAGVProBase.TEST_DATA_FILE, "stop")


@allure.feature("小车停止运动")
@allure.story("运动后小车停止运动")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "power_on"], ids=lambda c: c["title"])
def test_stop1(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    if case['ID'] == 1:
        with allure.step(f'机械臂向前运动'):
            device.mc.move_forward(case['parameters'])
    elif case['ID'] == 2:
        with allure.step(f'机械臂向后运动'):
            device.mc.move_backward(case['parameters'])
    elif case['ID'] == 3:
        with allure.step(f'机械臂左平移运动'):
            device.mc.move_left_lateral(case['parameters'])
    elif case['ID'] == 4:
        with allure.step(f'机械臂右平移运动'):
            device.mc.move_right_lateral(case['parameters'])
    elif case['ID'] == 5:
        with allure.step(f'机械臂左旋运动'):
            device.mc.turn_left(case['parameters'])
    elif case['ID'] == 6:
        with allure.step(f'机械臂右旋运动'):
            device.mc.turn_right(case['parameters'])

    input(f'确认小车是否运动, 回车测试继续')

    with allure.step(f'调用 {case["api"]} 接口'):
        response = device.mc.stop()
        logger.debug(f"接口返回：{response}")

    res = input(f'小车是否停止运动, 停止运动回车, 未停止运动输入1\n')
    with allure.step("断言小车是否停止运动"):
        assert res != '1', f"小车未停止运动, 期望 '', 实际 {res}"

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("小车停止运动")
@allure.story("下电后小车停止运动")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "power_off"], ids=lambda c: c["title"])
def test_stop2(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step(f"小车下电"):
        device.mc.power_off()

    with allure.step(f'调用 {case["api"]} 接口'):
        response = device.mc.stop()
        logger.debug(f"接口返回：{response}")

    with allure.step(f"小车上电"):
        device.mc.power_on()

    with allure.step("断言返回值类型"):
        assert response is None, f"机械臂返回类型错误，期望None，实际{type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')
