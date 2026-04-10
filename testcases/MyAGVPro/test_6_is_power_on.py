import time
import pytest
import allure
from pymycobot.error import MyCobotPro450DataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MyAGVProBase

# 从 Excel 读取测试数据
cases = get_test_data_from_excel(MyAGVProBase.TEST_DATA_FILE, "is_power_on")

@pytest.fixture(autouse=True)
def reset(device):
    # 每个用例后自动上电
    yield
    device.mc.power_on()

@allure.feature("主控是否上电")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_is_power_on1(device, case):
    title = case["title"]
    expected = case["expect_data"]

    logger.info(f'》》》》》用例【{title}】开始测试《《《《《')
    logger.debug(f'test_api:{case["api"]}')

    if case['ID'] == 1:
        with allure.step("机械臂上电"):
            device.mc.power_on()
    elif case['ID'] == 2:
        with allure.step("机械臂下电"):
            device.mc.power_off()
    elif case['ID'] == 3:
        input(f'拍下急停回车后继续测试')

    with allure.step(f"调用 {case['api']} 接口"):
        set_res = device.mc.is_power_on()
        logger.debug(f"接口返回：{set_res}")

    if case['ID'] == 3:
        input(f'松开急停回车后继续测试')

    with allure.step("断言返回值类型为 int"):
        assert isinstance(set_res, int), f"返回类型错误,应为{type(expected)},实际为 {type(set_res)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(set_res), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert set_res == expected, f"用例【{title}】断言失败，期望 {expected},实际 {set_res}"

    logger.info(f'✅ 用例【{title}】测试通过')
    logger.info(f'》》》》》用例【{case["title"]}】测试完成《《《《《')

