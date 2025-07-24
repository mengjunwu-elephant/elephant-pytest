import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "jog_coord")


@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.ml.power_on()
    dev.mr.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.go_zero()
    dev.mr.power_off()
    dev.ml.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")


@pytest.fixture(autouse=True)
def reset_coords(device):
    device.init_coords()
    yield


@allure.feature("jog_coord 接口测试")
@allure.story("正常功能验证")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "normal"], ids=lambda c: c["title"])
def test_jog_coord_normal(device, case):
    axis = case["axis"]
    param = case["parameter"]
    speed = case["speed"]
    title = case["title"]

    logger.info(f"》》》开始用例【{title}】《《《")
    logger.debug(f"Axis: {axis}, Param: {param}, Speed: {speed}")

    with allure.step("发送 jog_coord 指令（左臂）"):
        l_response = device.ml.jog_coord(axis, param, speed)

    with allure.step("发送 jog_coord 指令（右臂）"):
        r_response = device.mr.jog_coord(axis, param, speed)

    with allure.step("断言响应类型"):
        assert isinstance(l_response, int), f"左臂响应应为 int，实际为 {type(l_response)}"
        assert isinstance(r_response, int), f"右臂响应应为 int，实际为 {type(r_response)}"

    with allure.step("断言返回值正确"):
        assert l_response == case["l_expect_data"], f"左臂期望值：{case['l_expect_data']}，实际值：{l_response}"
        assert r_response == case["r_expect_data"], f"右臂期望值：{case['r_expect_data']}，实际值：{r_response}"

    logger.info(f"✅ 用例【{title}】通过")


@allure.feature("jog_coord 接口测试")
@allure.story("异常边界验证")
@pytest.mark.parametrize("case", [c for c in cases if c["test_type"] == "exception"], ids=lambda c: c["title"])
def test_jog_coord_exception(device, case):
    axis = case["axis"]
    param = case["parameter"]
    speed = case["speed"]
    title = case["title"]

    logger.info(f"》》》开始异常用例【{title}】《《《")
    logger.debug(f"Axis: {axis}, Param: {param}, Speed: {speed}")

    with allure.step("发送异常 jog_coord 指令并断言抛出 MercuryDataException"):
        with pytest.raises(MercuryDataException):
            device.ml.jog_coord(axis, param, speed)

    logger.info(f"✅ 异常用例【{title}】触发成功")
