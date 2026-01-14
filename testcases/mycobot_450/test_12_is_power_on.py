import pytest
import allure
from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import Mycobot450Base

cases = get_test_data_from_excel(Mycobot450Base.TEST_DATA_FILE, "is_power_on")

@pytest.fixture(scope="module")
def device():
    dev = Mycobot450Base()
    logger.info("初始化完成，接口测试开始")
    yield dev
    # 测试结束,恢复上电状态
    dev.mc.power_on()
    logger.info("环境清理完成，接口测试结束")

@pytest.fixture(autouse=True)
def reset_device(device):
    yield
    device.mc.power_on()

@allure.feature("机械臂电源状态查询")
@allure.story("查询上电状态")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_on"], ids=lambda c: c["title"])
def test_power_on(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")

    logger.debug(f'test_api: {case["api"]}')

    with allure.step("执行上电指令"):
        device.mc.power_on()

    with allure.step("左臂查询上电状态"):
        response = device.mc.is_power_on()

    with allure.step("断言返回类型"):
        assert isinstance(response, int), f"左臂返回类型错误：{type(response)}"

    with allure.step("断言返回结果"):
        allure.attach(str(case['expect_data']),name= "期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(response),name= "实际值",attachment_type= allure.attachment_type.TEXT)
        assert response == case["expect_data"], f"断言失败，期望：{case['expect_data']}，实际：{response}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("机械臂电源状态查询")
@allure.story("查询下电状态")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_off"], ids=lambda c: c["title"])
def test_power_off(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")

    logger.debug(f'test_api: {case["api"]}')

    with allure.step('执行下电指令'):
        device.mc.power_off()

    with allure.step("查询上电状态"):
        response = device.mc.is_power_on()

    with allure.step("断言返回类型"):
        assert isinstance(response, int), f"返回类型错误：{type(response)}"

    with allure.step("断言返回结果"):
        allure.attach(str(case['expect_data']),name='期望值',attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response),name='实际值',attachment_type=allure.attachment_type.TEXT)
        assert response == case["expect_data"], f"断言失败，期望：{case['expect_data']}，实际：{response}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("机械臂电源状态查询")
@allure.story("急停异常状态查询")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "emergency"], ids=lambda c: c["title"])
def test_emergency(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")

    logger.debug(f'test_api: {case["api"]}')

    input(print("请按下急停，点击回车后继续测试"))
    with allure.step("执行上电指令"):
        device.mc.power_on()

    with allure.step("左臂查询上电状态"):
        response = device.mc.is_power_on()

    input(print("请松开急停，点击回车后继续测试"))

    with allure.step("断言返回结果"):
        allure.attach(str(case['expect_data']),name='期望值',attachment_type=allure.attachment_type.TEXT)
        allure.attach(str(response),name='实际值',attachment_type=allure.attachment_type.TEXT)
        assert response == case["expect_data"], f"结果断言失败，期望：{case['expect_data']}，实际：{response}"

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")