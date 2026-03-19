import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_torque_comp")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("扭矩补偿接口")
@allure.story("获取扭矩补偿参数")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_get_torque_comp(device, case):
    title = case["title"]
    with allure.step(f"开始用例【{title}】"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        logger.debug(f"用例详情: {case}")

        with allure.step("调用机械臂 get_torque_comp 接口"):
            response = device.mc.get_torque_comp()
            logger.debug(f"机械臂响应: {response}")
        with allure.step("断言返回值类型"):
            assert isinstance(response, list), f"机械臂返回类型应为 list，实际为 {type(response)}"

        with allure.step("断言返回结果是否符合预期"):
            expected = eval(case["l_expect_data"])
            assert response == expected, f"机械臂期望值: {expected}, 实际值: {response}"

        logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")
