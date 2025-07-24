import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "set_max_speed")


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


@allure.feature("设置最大速度")
@allure.story("正常设置")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_max_speed_normal(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"API: {case['api']}")
    logger.debug(f"参数: {case['parameter']}，模式: {case['mode']}")

    with allure.step("发送 set_max_speed 指令"):
        l_response = device.ml.set_max_speed(case['mode'], case['parameter'])
        r_response = device.mr.set_max_speed(case['mode'], case['parameter'])

    with allure.step("响应类型断言"):
        assert isinstance(l_response, int), f"左臂返回类型应为 int，实际为 {type(l_response)}"
        assert isinstance(r_response, int), f"右臂返回类型应为 int，实际为 {type(r_response)}"

    with allure.step("响应值断言"):
        assert l_response == case['l_expect_data'], f"左臂返回值不符，期望：{case['l_expect_data']}，实际：{l_response}"
        assert r_response == case['r_expect_data'], f"右臂返回值不符，期望：{case['r_expect_data']}，实际：{r_response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("设置最大速度")
@allure.story("异常设置")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_max_speed_exception(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"API: {case['api']}")
    logger.debug(f"参数: {case['parameter']}，模式: {case['mode']}")

    with allure.step("断言抛出 MercuryDataException"):
        with pytest.raises(MercuryDataException,
                           match=".*",
                           message=f"用例【{title}】未触发 MercuryDataException，参数：{case['parameter']}，模式：{case['mode']}"):
            device.ml.set_max_speed(case["mode"], case["parameter"])
            device.mr.set_max_speed(case["mode"], case["parameter"])

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("设置最大速度")
@allure.story("保存与否验证")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "save_or_not"], ids=lambda c: c["title"])
def test_set_max_speed_save_or_not(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"API: {case['api']}")
    logger.debug(f"参数: {case['parameter']}，模式: {case['mode']}")

    with allure.step("设置最大速度"):
        l_response = device.ml.set_max_speed(case["mode"], case["parameter"])
        r_response = device.mr.set_max_speed(case["mode"], case["parameter"])

    with allure.step("重启设备"):
        device.reset()

    with allure.step("读取最大速度"):
        l_get_res = device.ml.get_max_speed(case["mode"])
        r_get_res = device.mr.get_max_speed(case["mode"])

    with allure.step("响应类型断言"):
        assert isinstance(l_response, int), f"左臂设置返回类型应为 int，实际为 {type(l_response)}"
        assert isinstance(r_response, int), f"右臂设置返回类型应为 int，实际为 {type(r_response)}"

    with allure.step("断言是否保存成功"):
        assert l_get_res == case["l_expect_data"], f"左臂读取值不符，期望：{case['l_expect_data']}，实际：{l_get_res}"
        assert r_get_res == case["r_expect_data"], f"右臂读取值不符，期望：{case['r_expect_data']}，实际：{r_get_res}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")
