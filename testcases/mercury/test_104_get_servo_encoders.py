import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 从Excel中提取数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_servo_encoders")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("舵机接口")
@allure.story("获取所有舵机编码器值")
@pytest.mark.parametrize("case", cases, ids=lambda c: c["title"])
def test_get_servo_encoders(device, case):
    title = case["title"]
    with allure.step(f"开始用例【{title}】"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        logger.debug(f"用例详情: {case}")

        with allure.step("调用机械臂 get_servo_encoders 接口"):
            response = device.mc.get_servo_encoders()
            logger.debug(f"机械臂响应: {response}")
        with allure.step("断言返回类型为 list"):
            assert isinstance(response, list), f"机械臂返回类型应为 list，实际为 {type(response)}"

        with allure.step("断言返回结果是否符合预期"):
            expected = eval(case["l_expect_data"])
            assert response == expected, f"机械臂期望: {expected}, 实际: {response}"

        logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")
