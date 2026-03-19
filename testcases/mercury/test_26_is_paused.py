import time

import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 加载用例数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "is_paused")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@pytest.fixture(autouse=True)
def setup_env(device):
    device.mc.set_limit_switch(2, 0)
    device.init_coords()
    yield
    device.go_zero()
    device.reset()

@allure.feature("is_paused 状态查询")
@allure.story("执行 pause 后查询状态")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_is_paused_after_pause(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")

    time.sleep(0.3)
    with allure.step("先调用 pause 进行暂停"):
        device.mc.pause()

    with allure.step("查询 is_paused 状态"):
        response = device.mc.is_paused()

    with allure.step("断言类型正确"):
        assert isinstance(response, int), f"机械臂类型错误: {type(response)}"

    with allure.step("断言返回值正确"):
        assert response == case["l_expect_data"], f"机械臂返回错误: {response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("is_paused 状态查询")
@allure.story("未调用 pause 直接查询")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal1"], ids=lambda c: c["title"])
def test_is_paused_without_pause(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")

    with allure.step("直接查询 is_paused 状态（未先 pause）"):
        response = device.mc.is_paused()

    with allure.step("断言类型正确"):
        assert isinstance(response, int), f"机械臂类型错误: {type(response)}"

    with allure.step("断言返回值正确"):
        assert response == case["l_expect_data"], f"机械臂返回错误: {response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")
