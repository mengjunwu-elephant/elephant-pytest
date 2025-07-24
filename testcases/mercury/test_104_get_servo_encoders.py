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
    dev.ml.power_on()
    dev.mr.power_on()
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

        with allure.step("调用左臂 get_servo_encoders 接口"):
            l_response = device.ml.get_servo_encoders()
            logger.debug(f"左臂响应: {l_response}")

        with allure.step("调用右臂 get_servo_encoders 接口"):
            r_response = device.mr.get_servo_encoders()
            logger.debug(f"右臂响应: {r_response}")

        with allure.step("断言返回类型为 list"):
            assert isinstance(l_response, list), f"左臂返回类型应为 list，实际为 {type(l_response)}"
            assert isinstance(r_response, list), f"右臂返回类型应为 list，实际为 {type(r_response)}"

        with allure.step("断言返回结果是否符合预期"):
            expected_l = eval(case["l_expect_data"])
            expected_r = eval(case["r_expect_data"])
            assert l_response == expected_l, f"左臂期望: {expected_l}, 实际: {l_response}"
            assert r_response == expected_r, f"右臂期望: {expected_r}, 实际: {r_response}"

        logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")
