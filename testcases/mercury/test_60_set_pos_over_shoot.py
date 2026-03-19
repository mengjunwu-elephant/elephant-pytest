import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "set_pos_over_shoot")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.set_default_pos_over_shoot()
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
@allure.feature("位置超调参数设置")
@allure.story("正常用例")
def test_set_pos_over_shoot_normal(device, case):
    title = case["title"]
    param = case["parameter"]

    with allure.step(f"用例【{title}】开始"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        logger.debug(f"参数: {param}")

        response = device.mc.set_pos_over_shoot(param)

        with allure.step("断言返回类型为int"):
            assert isinstance(response, int), f"机械臂返回类型错误: {type(response)}"

        with allure.step("断言返回值符合预期"):
            assert response == case["l_expect_data"], f"机械臂期望: {case['l_expect_data']}，实际: {response}"

        logger.info(f"用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")

@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
@allure.feature("位置超调参数设置")
@allure.story("异常用例")
def test_set_pos_over_shoot_exception(device, case):
    title = case["title"]
    param = case["parameter"]

    with allure.step(f"用例【{title}】开始"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        logger.debug(f"参数: {param}")

        with pytest.raises(MercuryDataException) as exc_info:
            device.mc.set_pos_over_shoot(param)

        logger.info(f"✅ 用例【{case['title']}】触发了预期异常: {exc_info.value}")
    logger.info(f"》》》用例【{title}】测试完成《《《")

