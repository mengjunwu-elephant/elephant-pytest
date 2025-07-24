import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "set_pos_over_shoot")


@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.ml.power_on()
    dev.mr.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.set_default_pos_over_shoot()
    dev.mr.power_off()
    dev.ml.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")


@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
@allure.feature("位置超调参数设置")
@allure.story("正常用例")
def test_set_pos_over_shoot_normal(device, case):
    title = case["title"]
    param = case["parameter"]

    with allure.step(f"用例【{title}】开始"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        logger.debug(f"参数: {param}")

        l_response = device.ml.set_pos_over_shoot(param)
        r_response = device.mr.set_pos_over_shoot(param)

        with allure.step("断言返回类型为int"):
            assert isinstance(l_response, int), f"左臂返回类型错误: {type(l_response)}"
            assert isinstance(r_response, int), f"右臂返回类型错误: {type(r_response)}"

        with allure.step("断言返回值符合预期"):
            assert r_response == case["r_expect_data"], f"右臂期望: {case['r_expect_data']}，实际: {r_response}"
            assert l_response == case["l_expect_data"], f"左臂期望: {case['l_expect_data']}，实际: {l_response}"

        logger.info(f"用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
@allure.feature("位置超调参数设置")
@allure.story("异常用例")
def test_set_pos_over_shoot_exception(device, case):
    title = case["title"]
    param = case["parameter"]

    with allure.step(f"用例【{title}】开始"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        logger.debug(f"参数: {param}")

        with pytest.raises(MercuryDataException):
            device.ml.set_pos_over_shoot(param)
        with pytest.raises(MercuryDataException):
            device.mr.set_pos_over_shoot(param)

        logger.info(f"用例【{title}】异常断言成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "save_or_not"], ids=lambda c: c["title"])
@allure.feature("位置超调参数设置")
@allure.story("保存与否测试")
def test_set_pos_over_shoot_save_or_not(device, case):
    title = case["title"]
    param = case["parameter"]

    with allure.step(f"用例【{title}】开始"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        logger.debug(f"参数: {param}")

        l_response = device.ml.set_pos_over_shoot(param)
        r_response = device.mr.set_pos_over_shoot(param)

        device.reset()

        l_get_res = device.ml.get_pos_over_shoot()
        r_get_res = device.mr.get_pos_over_shoot()

        with allure.step("断言返回类型为int"):
            assert isinstance(l_response, int), f"左臂返回类型错误: {type(l_response)}"
            assert isinstance(r_response, int), f"右臂返回类型错误: {type(r_response)}"

        with allure.step("断言重启后读取值是否符合预期"):
            assert r_get_res == case["r_expect_data"], f"右臂期望: {case['r_expect_data']}，实际: {r_get_res}"
            assert l_get_res == case["l_expect_data"], f"左臂期望: {case['l_expect_data']}，实际: {l_get_res}"

        logger.info(f"用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")
