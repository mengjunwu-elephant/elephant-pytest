import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 从Excel加载用例
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_servo_status")


@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.ml.power_on()
    dev.mr.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.mr.power_off()
    dev.ml.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("获取舵机状态")
@allure.story("正常用例 - 获取左右臂舵机状态")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_get_servo_status_normal(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"测试API: {case['api']}")
    logger.debug(f"测试参数: {case['parameter']}")

    with allure.step("获取左臂舵机状态"):
        l_response = device.ml.get_servo_status()

    with allure.step("获取右臂舵机状态"):
        r_response = device.mr.get_servo_status()

    with allure.step("断言返回类型为list"):
        assert isinstance(l_response, list), f"左臂返回类型错误：{type(l_response)}"
        assert isinstance(r_response, list), f"右臂返回类型错误：{type(r_response)}"

    with allure.step("断言返回结果与期望值一致"):
        assert r_response == case["r_expect_data"], f"右臂期望={case['r_expect_data']}，实际={r_response}"
        assert l_response == case["l_expect_data"], f"左臂期望={case['l_expect_data']}，实际={l_response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")
