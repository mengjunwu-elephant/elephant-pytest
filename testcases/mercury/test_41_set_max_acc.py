import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

# 从Excel中读取测试数据
cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "set_max_acc")


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


@allure.feature("设置最大加速度")
@allure.story("正常设置验证")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_max_acc_normal(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"API: {case['api']} | 参数: {case['parameter']}")

    with allure.step("发送 set_max_acc 请求"):
        l_res = device.ml.set_max_acc(case["mode"], case["parameter"])
        r_res = device.mr.set_max_acc(case["mode"], case["parameter"])

    with allure.step("类型断言"):
        assert isinstance(l_res, int), f"左臂返回类型应为 int，实际为 {type(l_res)}"
        assert isinstance(r_res, int), f"右臂返回类型应为 int，实际为 {type(r_res)}"

    with allure.step("结果断言"):
        assert l_res == case["l_expect_data"], f"左臂期望值：{case['l_expect_data']}，实际值：{l_res}"
        assert r_res == case["r_expect_data"], f"右臂期望值：{case['r_expect_data']}，实际值：{r_res}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("设置最大加速度")
@allure.story("异常参数验证")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_max_acc_exception(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"API: {case['api']} | 参数: {case['parameter']} | 模式: {case['mode']}")

    with allure.step("断言抛出 MercuryDataException"):
        with pytest.raises(MercuryDataException):
            device.ml.set_max_acc(case["mode"], case["parameter"])
            device.mr.set_max_acc(case["mode"], case["parameter"])

    logger.info(f"✅ 用例【{title}】异常断言通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("设置最大加速度")
@allure.story("保存验证")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "save_or_not"], ids=lambda c: c["title"])
def test_set_max_acc_persistence(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"API: {case['api']} | 参数: {case['parameter']} | 模式: {case['mode']}")

    with allure.step("设置 max_acc"):
        l_res = device.ml.set_max_acc(case["mode"], case["parameter"])
        r_res = device.mr.set_max_acc(case["mode"], case["parameter"])

    with allure.step("重启设备"):
        device.reset()

    with allure.step("读取重启后设置值"):
        l_get = device.ml.get_max_acc(case["mode"])
        r_get = device.mr.get_max_acc(case["mode"])

    with allure.step("类型断言"):
        assert isinstance(l_get, int), f"左臂读取类型错误：{type(l_get)}"
        assert isinstance(r_get, int), f"右臂读取类型错误：{type(r_get)}"

    with allure.step("值断言"):
        assert l_get == case["l_expect_data"], f"左臂断言失败，期望：{case['l_expect_data']}，实际：{l_get}"
        assert r_get == case["r_expect_data"], f"右臂断言失败，期望：{case['r_expect_data']}，实际：{r_get}"

    logger.info(f"✅ 用例【{title}】保存性验证通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")
