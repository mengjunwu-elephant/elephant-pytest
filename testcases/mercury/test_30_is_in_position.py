import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 从Excel中提取数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "is_in_position")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.go_zero()
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("is_in_position 接口测试")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] in ["normal","left","right"]], ids=lambda c: c["title"])
def test_is_in_position_normal(device, case):
    title = case["title"]
    param = eval(case["parameter"])
    mode = case["mode"]

    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"接口: {case['api']}，参数: {param}，模式: {mode}")

    with allure.step('使机械臂运动到初始点位'):
        device.mc.send_angles(device.coords_init_angles,device.speed)
        device.wait()
        if mode == 1:
            logger.info(f"当前机械臂坐标为{device.mc.get_coords()}")
        elif mode == 2:
            logger.info(f"当前机械臂坐标为{device.mc.get_base_coords()}")

    with allure.step("调用 is_in_position 接口（机械臂）"):
        response = device.mc.is_in_position(param, mode)

    with allure.step("断言返回类型为 int"):
        assert isinstance(response, int), f"机械臂返回类型错误: {type(response)}"

    with allure.step("断言返回值是否符合预期"):
        assert response == case["l_expect_data"], (
            f"机械臂期望值 {case['l_expect_data']}，实际为 {response}"
        )

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("is_in_position 接口测试")
@allure.story("异常参数测试")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "exception"], ids=lambda c: c["title"])
def test_is_in_position_exception(device, case):
    title = case["title"]
    param = eval(case["parameter"])
    mode = case["mode"]

    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"接口: {case['api']}，参数: {param}，模式: {mode}")

    with allure.step("断言抛出 MercuryDataException"):
        with pytest.raises(MercuryDataException) as exc_info:
            device.mc.is_in_position(param, mode)

    logger.info(f"✅ 用例【{case['title']}】触发了预期异常: {exc_info.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("is_in_position 接口测试")
@allure.story("仅上电 is_in_position 场景")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_on_only"], ids=lambda c: c["title"])
def test_power_on_only(device, case):
    title = case["title"]
    param = eval(case["parameter"])
    mode = case["mode"]

    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"接口: {case['api']}，参数: {param}，模式: {mode}")

    with allure.step("机械臂仅上电"):
        device.power_on_only()

    with allure.step("调用 is_in_position 接口"):
        response = device.mc.is_in_position(param, mode)
    with allure.step("机械臂断言返回类型"):
        assert response is None, f"机械臂返回类型错误，期望None，实际{type(response)}"
    with allure.step("机械臂断言返回结果"):
        allure.attach(str(case["l_expect_data"]),name= "机械臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(response),name= "机械臂实际值",attachment_type= allure.attachment_type.TEXT)
        assert response == case["l_expect_data"], f"机械臂断言失败，期望：{case['l_expect_data']}，实际：{response}"

    with allure.step("机械臂上电"):
        device.power_on()

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("is_in_position 接口测试")
@allure.story("下电 is_in_position 场景")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "power_off"], ids=lambda c: c["title"])
def test_power_off(device, case):
    title = case["title"]
    param = eval(case["parameter"])
    mode = case["mode"]

    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"接口: {case['api']}，参数: {param}，模式: {mode}")

    with allure.step("机械臂下电"):
        device.power_off()

    with allure.step("调用 is_in_position 接口"):
        response = device.mc.is_in_position(param, mode)
    with allure.step("机械臂断言返回类型"):
        assert response is None, f"机械臂返回类型错误，期望None，实际{type(response)}"
    with allure.step("机械臂断言返回结果"):
        allure.attach(str(case["l_expect_data"]),name= "机械臂期望值",attachment_type= allure.attachment_type.TEXT)
        allure.attach(str(response),name= "机械臂实际值",attachment_type= allure.attachment_type.TEXT)
        assert response == case["l_expect_data"], f"机械臂断言失败，期望：{case['l_expect_data']}，实际：{response}"

    with allure.step("机械臂上电"):
        device.power_on()

    logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")
