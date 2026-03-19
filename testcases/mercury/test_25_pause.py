import time

import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 从Excel中提取数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "pause")

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
def setup_and_teardown(device):
    device.mc.set_limit_switch(2, 0)
    device.init_coords()
    yield
    device.go_zero()
    device.reset()

@allure.feature("Pause 暂停功能")
@allure.story("正常参数调用")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_pause_normal(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"参数: {case['parameter']}")

    time.sleep(0.3)
    with allure.step("调用机械臂 pause"):
        response = device.mc.pause(case["parameter"])
    with allure.step("断言返回类型"):
        assert isinstance(response, int), f"机械臂返回类型错误: {type(response)}"

    with allure.step("断言期望结果"):
        assert response == case["l_expect_data"], f"机械臂结果不一致: {response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("Pause 暂停功能")
@allure.story("异常参数调用")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "exception"], ids=lambda c: c["title"])
def test_pause_exception(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"参数: {case['parameter']}")

    with allure.step("验证机械臂异常参数抛出 MercuryDataException"):
        with pytest.raises(MercuryDataException):
            device.mc.pause(case["parameter"])

    with allure.step("验证机械臂异常参数抛出 MercuryDataException"):
        with pytest.raises(MercuryDataException)as exc_info:
            device.mc.pause(case["parameter"])

    logger.info(f"✅ 用例【{case['title']}】触发了预期异常: {exc_info.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")
