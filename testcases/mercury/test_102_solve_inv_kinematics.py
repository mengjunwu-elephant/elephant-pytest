import pytest
import allure
from pymycobot.error import MercuryDataException

from common1 import logger
from common1.test_data_handler import get_test_data_from_excel
from settings import MercuryBase

cases = get_test_data_from_excel(MercuryBase.TEST_DATA_FILE, "solve_inv_kinematics")


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


@allure.feature("逆运动学计算")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "normal"], ids=lambda c: c["title"])
def test_solve_inv_kinematics_normal(device, case):
    title = case["title"]
    with allure.step(f"用例【{title}】开始测试"):
        logger.debug(f"API: {case['api']}")
        logger.debug(f"参数: {case['parameter']}, {case['parameter_1']}")

        l_response = device.ml.solve_inv_kinematics(case["parameter"], case["parameter_1"])
        r_response = device.mr.solve_inv_kinematics(case["parameter"], case["parameter_1"])

        with allure.step("断言左臂返回类型"):
            assert isinstance(l_response, int), f"左臂返回类型应为int，实际为：{type(l_response)}"
        with allure.step("断言右臂返回类型"):
            assert isinstance(r_response, int), f"右臂返回类型应为int，实际为：{type(r_response)}"

        with allure.step("断言左臂值"):
            assert l_response == case["l_expect_data"], f"左臂期望：{case['l_expect_data']}，实际：{l_response}"
        with allure.step("断言右臂值"):
            assert r_response == case["r_expect_data"], f"右臂期望：{case['r_expect_data']}，实际：{r_response}"

        logger.info(f"✅ 用例【{title}】测试通过")


@allure.feature("逆运动学计算-异常场景")
@pytest.mark.parametrize("case", [c for c in cases if c.get("test_type") == "exception"], ids=lambda c: c["title"])
def test_solve_inv_kinematics_exception(device, case):
    title = case["title"]
    with allure.step(f"用例【{title}】开始测试（异常分支）"):
        logger.debug(f"API: {case['api']}")
        logger.debug(f"参数: {case['parameter']}, {case['parameter_1']}")

        with allure.step("断言左臂抛出 MercuryDataException"):
            with pytest.raises(MercuryDataException):
                device.ml.solve_inv_kinematics(case["parameter"], case["parameter_1"])
        with allure.step("断言右臂抛出 MercuryDataException"):
            with pytest.raises(MercuryDataException):
                device.mr.solve_inv_kinematics(case["parameter"], case["parameter_1"])

        logger.info(f"✅ 异常用例【{title}】触发 MercuryDataException 成功")
