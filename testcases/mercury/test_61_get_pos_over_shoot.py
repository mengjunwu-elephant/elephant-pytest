import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_pos_over_shoot")


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


@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
@allure.feature("获取位置超调")
def test_get_pos_over_shoot(device, case):
    title = case["title"]
    with allure.step(f"用例【{title}】开始测试"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        logger.debug(f"test_api: {case['api']}")
        logger.debug(f"test_parameter: {case['parameter']}")

        l_response = device.ml.get_pos_over_shoot()
        r_response = device.mr.get_pos_over_shoot()

        with allure.step("断言返回类型为 float"):
            assert isinstance(l_response, float), f"左臂返回类型错误，实际类型：{type(l_response)}"
            assert isinstance(r_response, float), f"右臂返回类型错误，实际类型：{type(r_response)}"

        with allure.step("断言返回值符合预期"):
            assert r_response == case["r_expect_data"], f"右臂期望：{case['r_expect_data']}，实际：{r_response}"
            assert l_response == case["l_expect_data"], f"左臂期望：{case['l_expect_data']}，实际：{l_response}"

        logger.info(f"用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")
