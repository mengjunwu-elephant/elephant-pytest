import time
import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MyAGVProBase

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(MyAGVProBase.TEST_DATA_FILE, "power_on")

@pytest.fixture(autouse=True)
def reset(device):
    # 每个用例后自动上电
    yield
    device.mc.power_on()

@allure.feature("上电")
@allure.story("上下电时上电")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_power_on1(device, case):
    title = case["title"]
    expected = case["expect_data"]

    if case['ID'] == 1:
        with allure.step("机械臂上电"):
            device.mc.power_on()
    elif case['ID'] == 2:
        with allure.step("机械臂下电"):
            device.mc.power_off()
            time.sleep(1)

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("调用 power_on 接口"):
        response = device.mc.power_on()
        logger.debug(f"接口返回：{response}")

    res = input(f'查看车轮是否锁紧, 锁紧回车, 未锁紧输入1\n')

    with allure.step("断言小车车轮是否锁紧"):
        assert res != '1', f"小车车轮未锁紧，期望 1,实际 {res}"

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

@allure.feature("上电")
@allure.story("拍下急停时上电")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "exception"], ids=lambda c: c["title"])
def test_power_on2(device, case):
    title = case["title"]
    expected = case["expect_data"]

    input(f'拍下急停回车后继续测试')

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    with allure.step("调用 power_on 接口"):
        response = device.mc.power_on()
        logger.debug(f"接口返回：{response}")

    res = input(f'松开急停查看车轮是否锁紧, 锁紧回车, 未锁紧输入1\n')

    with allure.step("断言小车车轮是否锁紧"):
        assert res == '1', f"小车车轮锁紧，期望 1,实际 {res}"

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')