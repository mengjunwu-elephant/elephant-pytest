import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "set_torque_comp")


@pytest.fixture(scope="module")
def device():
    dev = MercuryBase()
    dev.ml.power_on()
    dev.mr.power_on()
    logger.info("初始化完成，接口测试开始")
    yield dev
    dev.set_default_torque_comp()
    dev.mr.power_off()
    dev.ml.power_off()
    dev.close()
    logger.info("环境清理完成，接口测试结束")


@allure.feature("扭矩补偿接口")
@allure.story("正常设置扭矩补偿")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_set_torque_comp(device, case):
    title = case["title"]
    with allure.step(f"开始用例【{title}】"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        logger.debug(f"用例详情: {case}")

        with allure.step("调用左臂 set_torque_comp 接口"):
            l_response = device.ml.set_torque_comp(case["joint"], case["parameter"])
            logger.debug(f"左臂响应: {l_response}")
        with allure.step("调用右臂 set_torque_comp 接口"):
            r_response = device.mr.set_torque_comp(case["joint"], case["parameter"])
            logger.debug(f"右臂响应: {r_response}")

        with allure.step("断言返回值类型"):
            assert isinstance(l_response, int), f"左臂返回类型应为 int，实际为 {type(l_response)}"
            assert isinstance(r_response, int), f"右臂返回类型应为 int，实际为 {type(r_response)}"

        with allure.step("断言返回结果是否符合预期"):
            assert r_response == case["r_expect_data"], f"右臂期望: {case['r_expect_data']}, 实际: {r_response}"
            assert l_response == case["l_expect_data"], f"左臂期望: {case['l_expect_data']}, 实际: {l_response}"

        logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("扭矩补偿接口")
@allure.story("异常参数测试")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_set_torque_comp_exception(device, case):
    title = case["title"]
    with allure.step(f"开始用例【{title}】"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        logger.debug(f"用例详情: {case}")

        with allure.step("断言左臂调用接口时抛出 MercuryDataException 异常"):
            with pytest.raises(MercuryDataException):
                device.ml.set_torque_comp(case["joint"], case["parameter"])

        with allure.step("断言右臂调用接口时抛出 MercuryDataException 异常"):
            with pytest.raises(MercuryDataException):
                device.mr.set_torque_comp(case["joint"], case["parameter"])

        logger.info(f"✅ 用例【{title}】异常断言成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")


@allure.feature("扭矩补偿接口")
@allure.story("保存与否测试")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "save_or_not"], ids=lambda c: c["title"])
def test_set_torque_comp_save_or_not(device, case):
    title = case["title"]
    with allure.step(f"开始用例【{title}】"):
        logger.info(f"》》》用例【{title}】开始测试《《《")
        logger.debug(f"用例详情: {case}")

        with allure.step("调用左臂 set_torque_comp 接口"):
            l_response = device.ml.set_torque_comp(case["joint"], case["parameter"])
            logger.debug(f"左臂响应: {l_response}")

        with allure.step("调用右臂 set_torque_comp 接口"):
            r_response = device.mr.set_torque_comp(case["joint"], case["parameter"])
            logger.debug(f"右臂响应: {r_response}")

        with allure.step("重启机械臂设备"):
            device.reset()

        with allure.step("获取左臂的扭矩补偿参数"):
            l_get_res = device.ml.get_torque_comp()
            logger.debug(f"左臂当前补偿参数: {l_get_res}")

        with allure.step("获取右臂的扭矩补偿参数"):
            r_get_res = device.mr.get_torque_comp()
            logger.debug(f"右臂当前补偿参数: {r_get_res}")

        with allure.step("断言响应类型"):
            assert isinstance(l_response, int), f"左臂返回类型应为 int，实际为 {type(l_response)}"
            assert isinstance(r_response, int), f"右臂返回类型应为 int，实际为 {type(r_response)}"

        with allure.step("断言实际获取值是否符合预期"):
            expected_l = eval(case["l_expect_data"])
            expected_r = eval(case["r_expect_data"])
            assert l_get_res == expected_l, f"左臂期望值: {expected_l}, 实际值: {l_get_res}"
            assert r_get_res == expected_r, f"右臂期望值: {expected_r}, 实际值: {r_get_res}"

        logger.info(f"✅ 用例【{title}】测试成功")
    logger.info(f"》》》用例【{title}】测试完成《《《")
