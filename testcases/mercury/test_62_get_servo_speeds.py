import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 从Excel加载用例
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_servo_speeds")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.mc.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mc.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")

@allure.feature("获取舵机速度")
@allure.story("正常用例 - 获取机械臂舵机速度")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_get_servo_speeds_normal(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"测试API: {case['api']}")
    logger.debug(f"测试参数: {case['parameter']}")

    with allure.step("获取机械臂舵机速度"):
        response = device.mc.get_servo_speeds()
    with allure.step("断言返回类型为list"):
        assert isinstance(response, list), f"机械臂返回类型错误：{type(response)}"

    with allure.step("断言返回结果与期望值一致"):
        assert response == eval(case["l_expect_data"]), f"机械臂期望={case['l_expect_data']}，实际={response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")
