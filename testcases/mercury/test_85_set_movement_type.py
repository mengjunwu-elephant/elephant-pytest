import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "set_movement_type")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    # 测试结束前，恢复默认运动模式
    dev.mc.set_movement_type(1)
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置运动模式")
@allure.story("正常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_movement_type_normal(device, case):
    title = case["title"]
    param = case["parameter"]

    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"test_api: set_movement_type, test_parameter: {param}")

    response = device.mc.set_movement_type(param)

    with allure.step("断言返回类型为int"):
        assert isinstance(response, int), f"机械臂返回类型错误: {type(response)}"

    with allure.step("断言返回结果"):
        assert response == case["l_expect_data"], f"机械臂期望: {case['l_expect_data']}，实际: {response}"

    logger.info(f"用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("设置运动模式")
@allure.story("异常用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_movement_type_exception(device, case):
    title = case["title"]
    param = case["parameter"]

    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"test_api: set_movement_type, test_parameter: {param}")

    with allure.step("断言异常抛出"):
        with pytest.raises(MercuryDataException) as exc_info:
            device.mc.set_movement_type(param)

    logger.info(f"✅ 用例【{case['title']}】触发了预期异常: {exc_info.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("设置运动模式")
@allure.story("保存与否用例")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "save_or_not"], ids=lambda c: c["title"])
def test_set_movement_type_save_or_not(device, case):
    title = case["title"]
    param = case["parameter"]

    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"test_api: set_movement_type, test_parameter: {param}")

    response = device.mc.set_movement_type(param)

    # 重启机械臂，刷新状态
    device.reset()

    get_res = device.mc.get_movement_type()

    with allure.step("断言返回类型"):
        assert isinstance(response, int), f"机械臂返回类型错误: {type(response)}"

    with allure.step("断言保存后获取的运动模式"):
        assert get_res == case["l_expect_data"], f"机械臂期望: {case['l_expect_data']}，实际: {get_res}"

    logger.info(f"用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")
