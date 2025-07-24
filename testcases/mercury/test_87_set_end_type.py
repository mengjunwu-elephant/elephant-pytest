import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "set_end_type")

@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.ml.power_on()
    dev.mr.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    # 测试结束复位
    dev.ml.set_end_type(0)
    dev.mr.set_end_type(0)
    dev.mr.power_off()
    dev.ml.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("设置末端类型")
@allure.story("正常用例 - 设置左右臂末端类型")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_end_type_normal(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"测试API: {case['api']}")
    logger.debug(f"测试参数: {case['parameter']}")

    with allure.step("设置左臂末端类型"):
        l_response = device.ml.set_end_type(case["parameter"])

    with allure.step("设置右臂末端类型"):
        r_response = device.mr.set_end_type(case["parameter"])

    with allure.step("断言返回类型为int"):
        assert isinstance(l_response, int), f"左臂返回类型错误：{type(l_response)}"
        assert isinstance(r_response, int), f"右臂返回类型错误：{type(r_response)}"

    with allure.step("断言返回结果与期望值一致"):
        assert l_response == case["l_expect_data"], f"左臂期望={case['l_expect_data']}，实际={l_response}"
        assert r_response == case["r_expect_data"], f"右臂期望={case['r_expect_data']}，实际={r_response}"

    logger.info(f"✅ 用例【{title}】测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("设置末端类型")
@allure.story("异常用例 - 设置末端类型异常输入")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_end_type_exception(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"测试API: {case['api']}")
    logger.debug(f"测试参数: {case['parameter']}")

    with allure.step("异常参数设置末端类型，应触发 MercuryDataException 异常"):
        with pytest.raises(MercuryDataException):
            device.ml.set_end_type(case["parameter"])
        with pytest.raises(MercuryDataException):
            device.mr.set_end_type(case["parameter"])

    logger.info(f"✅ 用例【{title}】异常测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("设置末端类型")
@allure.story("保存校验 - 设置末端类型后重启确认保存")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "save_or_not"], ids=lambda c: c["title"])
def test_set_end_type_save_or_not(device, case):
    title = case["title"]
    logger.info(f"》》》用例【{title}】开始测试《《《")
    logger.debug(f"测试API: {case['api']}")
    logger.debug(f"测试参数: {case['parameter']}")

    with allure.step("设置左臂末端类型"):
        l_response = device.ml.set_end_type(case["parameter"])

    with allure.step("设置右臂末端类型"):
        r_response = device.mr.set_end_type(case["parameter"])

    with allure.step("重启设备以确认保存"):
        device.reset()

    with allure.step("获取左臂末端类型确认保存"):
        l_get_res = device.ml.get_end_type()

    with allure.step("获取右臂末端类型确认保存"):
        r_get_res = device.mr.get_end_type()

    with allure.step("断言返回类型和保存结果"):
        assert isinstance(l_response, int), f"左臂返回类型错误：{type(l_response)}"
        assert isinstance(r_response, int), f"右臂返回类型错误：{type(r_response)}"
        assert l_get_res == case["l_expect_data"], f"左臂期望={case['l_expect_data']}，实际={l_get_res}"
        assert r_get_res == case["r_expect_data"], f"右臂期望={case['r_expect_data']}，实际={r_get_res}"

    logger.info(f"✅ 用例【{title}】保存校验测试通过")
    logger.info(f"》》》用例【{title}】测试完成《《《")
