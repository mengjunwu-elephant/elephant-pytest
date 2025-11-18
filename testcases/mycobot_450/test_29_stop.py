import time

import pytest
import allure
from pymycobot.error import MyCobotPro450DataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot450Base

# 从Excel中提取数据
cases = get_test_data_from_excel(Mycobot450Base.TEST_DATA_FILE, "stop")


@pytest.fixture(scope="module")
def device():
    dev = Mycobot450Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.default_settings()
    dev.go_zero()
    dev.wait()
    #dev.mc.close()
    logger.info("环境清理完成，接口测试结束")

@pytest.fixture(autouse=True)
def reset_device(device):
    yield
    device.go_zero()
    device.wait()

@allure.feature("stop 接口测试")
@allure.story("正常 stop 场景")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_stop_normal(device, case):
    title = case["title"]
    expected = case["expect_data"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"接口: {case['api']}，参数: {case['parameter']}")

    with allure.step('使机械臂运动'):
        device.mc.send_angles(device.coords_init_angles,device.speed)
        time.sleep(0.5)

    with allure.step("调用 stop 接口"):
        response = device.mc.stop(case["parameter"])

    with allure.step("断言返回值类型为 int"):
        assert isinstance(response, int), f"返回类型错误,应为{type(expected)},实际为 {type(response)}"

    with allure.step("断言接口返回结果"):
        allure.attach(str(expected), name="期望值", attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response), name="实际值", attachment_type=allure.attachment_type.TEXT)
        assert response == expected, f"用例【{title}】断言失败，期望 {expected},实际 {response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("stop 接口测试")
@allure.story("异常参数校验")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "exception"], ids=lambda c: c["title"])
def test_stop_exception(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"接口: {case['api']}，参数: {case['parameter']}")

    with allure.step("调用 stop 接口并断言抛出 MyCobotPro450DataException"):
        with pytest.raises(MyCobotPro450DataException):
            device.mc.stop(case["parameter"])

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")