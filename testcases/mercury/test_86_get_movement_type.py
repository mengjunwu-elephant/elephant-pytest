import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_movement_type")


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


@allure.feature("获取运动模式")
@pytest.mark.parametrize("case", cases, ids=lambda c: c["title"])
def test_get_movement_type(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"test_api: {case['api']}")

    l_response = device.ml.get_movement_type()
    r_response = device.mr.get_movement_type()

    with allure.step("断言返回类型"):
        assert isinstance(l_response, int), f"左臂返回类型错误，实际类型：{type(l_response)}"
        assert isinstance(r_response, int), f"右臂返回类型错误，实际类型：{type(r_response)}"

    with allure.step("断言返回结果"):
        try:
            assert l_response == case['l_expect_data']
            assert r_response == case['r_expect_data']
        except AssertionError:
            logger.error(f"断言失败: 用例【{title}]")
            logger.debug(f"左臂期望：{case['l_expect_data']}，实际：{l_response}")
            logger.debug(f"右臂期望：{case['r_expect_data']}，实际：{r_response}")
            raise

    logger.info(f"用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")
