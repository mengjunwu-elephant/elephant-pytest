import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "set_end_type")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    # 测试结束复位
    dev.mc.set_end_type(0)
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("设置末端类型")
@allure.story("正常用例 - 设置机械臂末端类型")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_end_type_normal(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"测试API: {case['api']}")
    logger.debug(f"测试参数: {case['parameter']}")

    with allure.step("设置机械臂末端类型"):
        response = device.mc.set_end_type(case["parameter"])
    with allure.step("断言返回类型为int"):
        assert isinstance(response, int), f"机械臂返回类型错误：{type(response)}"

    with allure.step("断言返回结果与期望值一致"):
        assert response == case["l_expect_data"], f"机械臂期望={case['l_expect_data']}，实际={response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@allure.feature("设置末端类型")
@allure.story("异常用例 - 设置末端类型异常输入")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_end_type_exception(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"测试API: {case['api']}")
    logger.debug(f"测试参数: {case['parameter']}")

    with allure.step("异常参数设置末端类型，应触发 MercuryDataException 异常"):
        with pytest.raises(MercuryDataException) as exc_info:
            device.mc.set_end_type(case["parameter"])

    logger.info(f"✅ 用例【{case['title']}】触发了预期异常: {exc_info.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")
