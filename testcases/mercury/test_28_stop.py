import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 从Excel中提取数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "stop")


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


@pytest.fixture(autouse=True)
def setup_env(device):
    device.ml.set_limit_switch(2, 0)
    device.mr.set_limit_switch(2, 0)
    device.init_coords()
    yield
    device.go_zero()
    device.reset()


@allure.feature("stop 接口测试")
@allure.story("正常 stop 场景")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_stop_normal(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"接口: {case['api']}，参数: {case['parameter']}")

    with allure.step("调用 stop 接口"):
        l_response = device.ml.stop(case["parameter"])
        r_response = device.mr.stop(case["parameter"])

    with allure.step("断言返回类型为 int"):
        assert isinstance(l_response, int), f"左臂返回类型错误: {type(l_response)}"
        assert isinstance(r_response, int), f"右臂返回类型错误: {type(r_response)}"

    with allure.step("断言返回值是否正确"):
        assert l_response == case["l_expect_data"], f"左臂返回值错误: {l_response}"
        assert r_response == case["r_expect_data"], f"右臂返回值错误: {r_response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("stop 接口测试")
@allure.story("异常参数校验")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "exception"], ids=lambda c: c["title"])
def test_stop_exception(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"接口: {case['api']}，参数: {case['parameter']}")

    with allure.step("调用 stop 接口并断言抛出 MercuryDataException"):
        with pytest.raises(MercuryDataException):
            device.ml.stop(case["parameter"])
            device.mr.stop(case["parameter"])

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")
