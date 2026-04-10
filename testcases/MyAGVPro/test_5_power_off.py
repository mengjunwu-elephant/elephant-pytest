import time
import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MyAGVProBase

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(MyAGVProBase.TEST_DATA_FILE, "power_off")

@pytest.fixture(autouse=True)
def reset(device):
    # 每个用例后自动上电
    yield
    device.mc.power_on()

@allure.feature("下电")
@allure.story("上下电时下电")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_power_off1(device, case):
    title = case["title"]
    expected = case["expect_data"]

    if case['ID'] == 1:
        with allure.step("机械臂上电"):
            device.mc.power_on()
    elif case['ID'] == 2:
        with allure.step("机械臂下电"):
            device.mc.power_off()

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("调用 power_off 接口"):
        response = device.mc.power_off()
        logger.debug(f"接口返回：{response}")

    with allure.step("调用运动接口"):
        device.mc.move_forward(device.speed)

    res = input(f'查看小车是否运动, 车轮是否锁紧, 锁紧运动回车, 未锁紧未运动输入1\n')

    with allure.step("断言小车是否运动"):
        assert res == '1', f"小车运动，期望 1,实际 {res}"

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("下电")
@allure.story("拍下急停时下电")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "exception"], ids=lambda c: c["title"])
def test_power_off2(device, case):
    title = case["title"]
    expected = case["expect_data"]

    input(f'拍下急停回车后继续测试')

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("调用 power_off 接口"):
        response = device.mc.power_off()
        logger.debug(f"接口返回：{response}")

    with allure.step("调用运动接口"):
        device.mc.move_forward(device.speed)

    res = input(f'松开急停查看小车是否运动, 车轮是否锁紧, 锁紧运动回车, 未锁紧未运动输入1\n')

    with allure.step("断言小车是否运动"):
        assert res == '1', f"小车运动，期望 1,实际 {res}"

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')