import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 读取测试数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "get_max_speed")


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


@allure.feature("获取最大速度")
@allure.story("正常参数")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_get_max_speed_normal(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"API: {case['api']}")
    logger.debug(f"参数: {case['parameter']}")

    with allure.step("发送 get_max_speed 指令"):
        l_response = device.ml.get_max_speed(case["parameter"])
        r_response = device.mr.get_max_speed(case["parameter"])

    with allure.step("断言返回类型"):
        assert isinstance(l_response, int), f"左臂返回类型应为 int，实际为 {type(l_response)}"
        assert isinstance(r_response, int), f"右臂返回类型应为 int，实际为 {type(r_response)}"

    with allure.step("断言返回值"):
        assert l_response == case["l_expect_data"], f"左臂返回值不符，期望：{case['l_expect_data']}，实际：{l_response}"
        assert r_response == case["r_expect_data"], f"右臂返回值不符，期望：{case['r_expect_data']}，实际：{r_response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("获取最大速度")
@allure.story("异常参数")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_get_max_speed_exception(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"API: {case['api']}")
    logger.debug(f"参数: {case['parameter']}")

    with allure.step("断言抛出 MercuryDataException 异常"):
        with pytest.raises(MercuryDataException,
                           match=".*",
                           message=f"用例【{title}】未触发 MercuryDataException，参数：{case['parameter']}"):
            device.ml.get_max_speed(case["parameter"])
            device.mr.get_max_speed(case["parameter"])

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")
