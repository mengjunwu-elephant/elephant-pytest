import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_model_direction")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@pytest.mark.parametrize("case", cases, ids=lambda c: c["title"])
@allure.feature("获取模型方向")
def test_get_model_direction(device, case):
    title = case["title"]
    with allure.step(f"用例【{title}】开始测试"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        logger.debug(f"API: {case['api']}")

        response = device.mc.get_model_direction()

        with allure.step("断言机械臂返回类型为 list"):
            assert isinstance(response, list), f"机械臂返回类型错误，实际为 {type(response)}"
            logger.debug("机械臂请求类型断言成功")

        with allure.step("断言机械臂返回类型为 list"):
            logger.debug("机械臂请求类型断言成功")

        expected = eval(case['l_expect_data'])

        with allure.step("断言机械臂返回值"):
            assert response == expected, f"机械臂期望：{expected}，实际：{response}"
        logger.info(f"✅ 用例【{title}】测试成功")
        logger.info(f"》》》用例【{title}】测试完成《《《")
