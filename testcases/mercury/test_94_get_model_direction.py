import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_model_direction")


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


@pytest.mark.parametrize("case", cases, ids=lambda c: c["title"])
@allure.feature("获取模型方向")
def test_get_model_direction(device, case):
    title = case["title"]
    with allure.step(f"用例【{title}】开始测试"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        logger.debug(f"API: {case['api']}")

        l_response = device.ml.get_model_direction()
        r_response = device.mr.get_model_direction()

        with allure.step("断言左臂返回类型为 list"):
            assert isinstance(l_response, list), f"左臂返回类型错误，实际为 {type(l_response)}"
            logger.debug("左臂请求类型断言成功")

        with allure.step("断言右臂返回类型为 list"):
            assert isinstance(r_response, list), f"右臂返回类型错误，实际为 {type(r_response)}"
            logger.debug("右臂请求类型断言成功")

        expected_l = eval(case['l_expect_data'])
        expected_r = eval(case['r_expect_data'])

        with allure.step("断言左臂返回值"):
            assert l_response == expected_l, f"左臂期望：{expected_l}，实际：{l_response}"

        with allure.step("断言右臂返回值"):
            assert r_response == expected_r, f"右臂期望：{expected_r}，实际：{r_response}"

        logger.info(f"✅ 用例【{title}】测试成功")
        logger.info(f"》》》用例【{title}】测试完成《《《")
