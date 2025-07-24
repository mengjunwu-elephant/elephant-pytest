import pytest
import allure

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 获取测试数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_coords")


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


@allure.feature("get_coords 接口测试")
@allure.story("获取末端位姿 - 正常场景")
@pytest.mark.parametrize("case", cases, ids=lambda c: c["title"])
def test_get_coords(device, case):
    logger.info(f"》》》》》用例【{case['title']}】开始测试《《《《《")
    allure.dynamic.title(case["title"])

    with allure.step("调试信息记录"):
        logger.debug("test_api: {}".format(case["api"]))
        logger.debug("test_parameter: {}".format(case["parameter"]))

    with allure.step("左臂请求发送"):
        l_response = device.ml.get_coords(eval(case['parameter']))
        logger.debug(f"左臂返回值: {l_response}")

    with allure.step("右臂请求发送"):
        r_response = device.mr.get_coords(eval(case['parameter']))
        logger.debug(f"右臂返回值: {r_response}")

    with allure.step("类型断言"):
        assert isinstance(l_response, list), f"左臂返回类型错误，实际为: {type(l_response)}"
        assert isinstance(r_response, list), f"右臂返回类型错误，实际为: {type(r_response)}"

    with allure.step("数据断言"):
        assert l_response == eval(case["l_expect_data"]), \
            f"左臂数据不一致：期望 {case['l_expect_data']}，实际 {l_response}"
        assert r_response == eval(case["r_expect_data"]), \
            f"右臂数据不一致：期望 {case['r_expect_data']}，实际 {r_response}"

    logger.info(f"✅ 用例【{case['title']}】测试通过")
